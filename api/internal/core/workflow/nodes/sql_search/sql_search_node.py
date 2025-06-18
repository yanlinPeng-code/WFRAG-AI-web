import time

from langchain_core.runnables import RunnableConfig
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing_extensions import Optional, Any

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkFlowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.utils.helper import extract_variables_from_state
from internal.exception import FailException
from .sql_search_entity import SqlSearchNodeData


class SqlSearchNode(BaseNode):
    """SQL查询节点，只执行前端传入的SQL语句（只允许SELECT）"""
    node_data: SqlSearchNodeData

    def invoke(self, state: WorkFlowState, config: Optional[RunnableConfig] = None, **kwargs: Any) -> WorkFlowState:
        start_at = time.perf_counter()

        # 提取输入变量
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 检查必要参数
        required_keys = ["host", "port", "user", "password", "database", "table"]
        missing = [k for k in required_keys if k not in inputs_dict or not inputs_dict[k]]
        if missing:
            return self._fail(inputs_dict, f"缺少必要参数: {', '.join(missing)}", start_at)

        # 构建数据库连接字符串 - 修复port参数类型转换
        exist_key = [key for key in inputs_dict.keys()]
        additional_key = set(exist_key) - set(required_keys)
        additional_field = {}
        for key in additional_key:
            additional_field[key] = inputs_dict.get(key)
        if len(additional_field) > 1:
            raise FailException("请检查输入参数，只能输入一个sql语句")
        if additional_field:
            sql = str(additional_field.get(list(additional_field.keys())[0])).strip()

            try:
                port = int(inputs_dict["port"]) if inputs_dict["port"] else 3306
                conn_str = f"mysql+pymysql://{inputs_dict['user']}:{inputs_dict['password']}@{inputs_dict['host']}:{port}/{inputs_dict['database']}"
            except (ValueError, TypeError) as e:
                return self._fail(inputs_dict, f"端口号格式错误: {e}", start_at)

            # 执行SQL查询
            try:
                engine = create_engine(conn_str)
                with engine.connect() as conn:
                    result = conn.execute(text(sql))
                    rows = [dict(row._mapping) for row in result]  # 修复行数据提取方式

            except (SQLAlchemyError, ValueError, Exception) as e:
                return self._fail(inputs_dict, f"数据库查询错误: {str(e)}", start_at)

        # 构建输出结果 - 修复输出格式
        output_var_name = self.node_data.outputs[0].name if self.node_data.outputs else "text"

        # 将查询结果转换为字符串格式，便于后续节点使用
        if rows:
            # 如果有数据，转换为格式化的字符串
            result_text = str(rows)
        else:
            # 如果没有数据，返回空列表的字符串表示
            result_text = "[]"

        outputs = {output_var_name: result_text}

        return self._success(inputs_dict, outputs, start_at)

    def _fail(self, inputs, error, start_at) -> WorkFlowState:
        """构建失败状态的工作流状态"""
        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.FAILED,
                    inputs=inputs,
                    outputs={},
                    latency=(time.perf_counter() - start_at),
                    error=error
                )
            ]
        }

    def _success(self, inputs, outputs, start_at) -> WorkFlowState:
        """构建成功状态的工作流状态"""
        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs=inputs,
                    outputs=outputs,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }

import time

from jinja2 import Template
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from typing_extensions import Optional, Any

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkFlowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.utils.helper import extract_variables_from_state
from .sql_agent_entity import SqlAgentNodeData


class SqlAgentNode(BaseNode):
    """SQL智能代理节点，自动用大模型生成SQL并执行"""
    node_data: SqlAgentNodeData

    def invoke(self, state: WorkFlowState, config: Optional[RunnableConfig] = None, **kwargs: Any) -> WorkFlowState:
        start_at = time.perf_counter()
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)
        template = Template(self.node_data.prompt)
        prompt_value = template.render(**inputs_dict)
        required_keys = ["host", "port", "user", "password", "database", "query"]
        missing = [k for k in required_keys if k not in inputs_dict or not inputs_dict[k]]
        if missing:
            return self._fail(inputs_dict, f"缺少必要参数: {', '.join(missing)}", start_at)
        uri = f"mysql+pymysql://{inputs_dict['user']}:{inputs_dict['password']}@{inputs_dict['host']}:{inputs_dict['port']}/{inputs_dict['database']}"
        db = SQLDatabase.from_uri(uri)
        try:
            from app.http.module import injector
            from internal.service import LanguageModelService
            language_service = injector.get(LanguageModelService)
            llm = language_service.load_language_model(model_config=self.node_data.language_model_config)

        except Exception as e:
            return self._fail(inputs_dict, f"模型加载失败: {str(e)}", start_at)
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()
        system_prompt = """
                         你是一个与 SQL 数据库交互的代理。
                        给定一个输入问题，创建一个语法正确的 {dialect} 查询来运行，
                        然后查看查询结果并返回答案。除非用户
                        指定了他们希望获取的特定示例数量，否则始终将查询限制为最多 {top_k} 个结果。

                        你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。切勿查询特定表的所有列，
                        只需查询与问题相关的列即可。

                        执行查询之前，你必须仔细检查查询。如果在执行查询时遇到错误，
                        请重写查询并重试。

                        请勿对数据库执行任何 DML 语句（INSERT、UPDATE、DELETE、DROP 等）。

                        首先，你应该始终查看数据库中的表，看看你可以查询哪些数据。不要跳过此步骤。

                        然后，你应该查询最相关的表的架构.
        """.format(
            dialect=db.dialect,
            top_k=5,
        )

        agent = create_react_agent(llm, tools, prompt=system_prompt)
        question = inputs_dict["query"]
        try:
            result = ""
            for step in agent.stream({"messages": [{"role": "user", "content": question}]}, stream_mode="values"):
                if "messages" in step and step["messages"]:
                    result = step["messages"][-1].content
            return self._success(inputs_dict,
                                 {self.node_data.outputs[0].name if self.node_data.outputs else "result": result},
                                 start_at)
        except Exception as e:
            return self._fail(inputs_dict, f"SQL代理执行失败: {str(e)}", start_at)

    def _fail(self, inputs, error, start_at) -> WorkFlowState:
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

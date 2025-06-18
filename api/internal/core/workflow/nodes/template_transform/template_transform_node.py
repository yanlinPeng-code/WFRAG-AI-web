import time

from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from typing_extensions import Optional, Any

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkFlowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.utils.helper import extract_variables_from_state
from .template_transform_entity import TemplateTransformNodeData


class TemplateTransformNode(BaseNode):
    node_data: TemplateTransformNodeData

    def invoke(
            self, state: WorkFlowState, config: Optional[RunnableConfig] = None, **kwargs: Any) -> WorkFlowState:
        """模板转换节点执行函数，将传递的多个变量合并成字符串后返回"""
        # 1.提取节点中的输入数据
        start_at = time.perf_counter()
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 2.使用jinja2格式模板信息
        template = Template(self.node_data.template)
        template_value = template.render(**inputs_dict)

        # 3.提取并构建输出数据结构
        outputs = {"output": template_value}

        # 4.构建响应状态并返回
        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs=inputs_dict,
                    outputs=outputs,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }

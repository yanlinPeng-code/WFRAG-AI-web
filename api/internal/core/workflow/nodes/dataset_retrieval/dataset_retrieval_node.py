import time
from uuid import UUID

from flask import Flask
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr
from typing_extensions import Optional, Any

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkFlowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.utils.helper import extract_variables_from_state
from .dataset_retrieval_entity import DatasetRetrievalNodeData


class DatasetRetrievalNode(BaseNode):
    """知识库检索节点"""
    node_data: DatasetRetrievalNodeData
    _retrieval_tool: BaseTool = PrivateAttr(None)

    def __init__(self,
                 *args: Any,
                 flask_app: Flask,
                 account_id: UUID,
                 **kwargs):
        super().__init__(*args, **kwargs)

        from app.http.app import injector
        from internal.service import RetrievalService
        retrieval_service = injector.get(RetrievalService)

        self._retrieval_tool = retrieval_service.create_langchain_tool_from_search(
            flask_app=flask_app,
            dataset_ids=self.node_data.dataset_ids,
            account_id=account_id,
            **self.node_data.retrieval_config.model_dump(),
        )

    def invoke(self, state: WorkFlowState, config: Optional[RunnableConfig] = None, **kwargs: Any) -> WorkFlowState:
        """知识库检索节点调用函数，执行响应的知识库检索后返回"""
        start_at = time.perf_counter()
        input_dict = extract_variables_from_state(self.node_data.inputs, state)

        combine_documents = self._retrieval_tool.invoke(input_dict)
        outputs = {}

        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = combine_documents
        else:
            outputs["combine_documents"] = combine_documents

        # 4.返回响应状态
        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs=input_dict,
                    outputs=outputs,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }

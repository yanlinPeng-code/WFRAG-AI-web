import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from flask import current_app
from injector import inject
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from internal.core.agent.agents import FunctionCallAgent, AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import QueueEvent
from internal.core.language_model.entities.model_entity import ModelFeature
# from internal.core.language_model.providers.tongyi.chat import Chat
from internal.core.language_model.providers.openai.chat import Chat
from internal.core.memory.token_buffer_memory import TokenBufferMemory
from internal.entity.conversation_entity import InvokeFrom, MessageStatus
from internal.model import Account, Message
from internal.schema.assistant_agent_schema import AssistantAgentChat, GetAssistantAgentMessagesWithPageReq
from internal.task.app_task import auto_create_app
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .conversation_service import ConversationService
from .faiss_service import FaissService
from .overflow_run import SynchronizedStructuredTool


@inject
@dataclass
class AssistantAgentService(BaseService):
    db: SQLAlchemy
    faiss_service: FaissService
    conversation_service: ConversationService

    def assistant_agent_chat(self, req: AssistantAgentChat, account: Account):
        """传递query与账号实现与辅助Agent进行会话"""
        # 1.获取辅助Agent对应的id
        assistant_agent_id = current_app.config.get("ASSISTANT_AGENT_ID")

        # 2.获取当前应用的调试会话信息
        conversation = account.assistant_agent_conversation

        # 3.新建一条消息记录
        message = self.create(
            Message,
            app_id=assistant_agent_id,
            conversation_id=conversation.id,
            invoke_from=InvokeFrom.DEBUGGER,
            created_by=account.id,
            query=req.query.data,
            image_urls=req.image_urls.data,
            status=MessageStatus.NORMAL,
        )

        # 4.使用GPT模型作为辅助Agent的LLM大脑
        llm = Chat(
            model="gpt-4o-mini",
            temperature=0.8,
            features=[ModelFeature.TOOL_CALL, ModelFeature.AGENT_THOUGHT, ModelFeature.IMAGE_INPUT],
            metadata={},
        )

        # 5.实例化TokenBufferMemory用于提取短期记忆
        token_buffer_memory = TokenBufferMemory(
            db=self.db,
            conversation=conversation,
            model_instance=llm,
        )
        history = token_buffer_memory.get_history_prompt_messages(message_limit=3)

        # 6.将草稿配置中的tools转换成LangChain工具
        tools = [
            self.faiss_service.convert_faiss_to_tool(),
            self.convert_create_app_to_tool(account.id),
        ]

        # 7.构建Agent智能体，使用FunctionCallAgent
        agent = FunctionCallAgent(
            llm=llm,
            agent_config=AgentConfig(
                user_id=account.id,
                invoke_from=InvokeFrom.ASSISTANT_AGENT,
                enable_long_term_memory=True,
                tools=tools,
            ),
        )

        agent_thoughts = {}
        for agent_thought in agent.stream({
            "messages": [llm.convert_to_human_message(req.query.data, req.image_urls.data)],
            "history": history,
            "long_term_memory": conversation.summary,
        }):
            # 8.提取thought以及answer
            event_id = str(agent_thought.id)

            # 9.将数据填充到agent_thought，便于存储到数据库服务中
            if agent_thought.event != QueueEvent.PING:
                # 10.除了agent_message数据为叠加，其他均为覆盖
                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    if event_id not in agent_thoughts:
                        # 11.初始化智能体消息事件
                        agent_thoughts[event_id] = agent_thought
                    else:
                        # 12.叠加智能体消息
                        agent_thoughts[event_id] = agent_thoughts[event_id].model_copy(update={
                            "thought": agent_thoughts[event_id].thought + agent_thought.thought,
                            # 消息相关数据
                            "message": agent_thought.message,
                            "message_token_count": agent_thought.message_token_count,
                            "message_unit_price": agent_thought.message_unit_price,
                            "message_price_unit": agent_thought.message_price_unit,
                            # 答案相关字段
                            "answer": agent_thoughts[event_id].answer + agent_thought.answer,
                            "answer_token_count": agent_thought.answer_token_count,
                            "answer_unit_price": agent_thought.answer_unit_price,
                            "answer_price_unit": agent_thought.answer_price_unit,
                            # Agent推理统计相关
                            "total_token_count": agent_thought.total_token_count,
                            "total_price": agent_thought.total_price,
                            "latency": agent_thought.latency,
                        })
                else:
                    # 13.处理其他类型事件的消息
                    agent_thoughts[event_id] = agent_thought
            data = {
                **agent_thought.model_dump(include={
                    "event", "thought", "observation", "tool", "tool_input", "answer", "latency",
                    "total_token_count",
                }),
                "id": event_id,
                "conversation_id": str(conversation.id),
                "message_id": str(message.id),
                "task_id": str(agent_thought.task_id),
            }
            yield f"event: {agent_thought.event}\ndata:{json.dumps(data)}\n\n"

        # 22.将消息以及推理过程添加到数据库
        self.conversation_service.save_agent_thoughts(
            account_id=account.id,
            app_id=assistant_agent_id,
            app_config={"long_term_memory": {"enable": True}},
            conversation_id=conversation.id,
            message_id=message.id,
            agent_thoughts=[agent_thought for agent_thought in agent_thoughts.values()],
        )

    def stop_chat(self, task_id: UUID, current_user: Account):
        pass
        """根据传递的任务id+账号停止某次响应会话"""
        AgentQueueManager.set_stop_flag(task_id, InvokeFrom.ASSISTANT_AGENT, current_user.id)

    def get_conversation_messages_with_page(self, req: GetAssistantAgentMessagesWithPageReq, current_user: Account):
        """根据传递的请求+账号获取与辅助Agent对话的消息分页列表"""
        # 1.获取应用的调试会话
        conversation = current_user.assistant_agent_conversation

        # 2.构建分页器并构建游标条件
        paginator = Paginator(db=self.db, req=req)
        filters = []
        if req.created_at.data:
            # 3.将时间戳转换成DateTime
            created_at_datetime = datetime.fromtimestamp(req.created_at.data)
            filters.append(Message.created_at <= created_at_datetime)

        # 4.执行分页并查询数据
        messages = paginator.paginate(
            self.db.session.query(Message).options(joinedload(Message.agent_thoughts)).filter(
                Message.conversation_id == conversation.id,
                Message.status.in_([MessageStatus.STOP, MessageStatus.NORMAL]),
                Message.answer != "",
                *filters,
            ).order_by(desc("created_at"))
        )

        return messages, paginator

    def delete_conversation(self, current_user: Account):
        self.update(current_user, assistant_agent_conversation_id=None)

    @classmethod
    def convert_create_app_to_tool(cls, account_id: UUID) -> BaseTool:
        """定义自动创建Agent应用LangChain工具"""

        class CreateAppInput(BaseModel):
            """创建Agent/应用输入结构"""
            name: str = Field(description="需要创建的Agent/应用名称，长度不超过50个字符")
            description: str = Field(description="需要创建的Agent/应用描述，请详细概括该应用的功能")

        def create_app(name: str, description: str, callbacks: Optional[CallbackManagerForToolRun] = None, **kwargs):
            # 1.调用celery异步任务在后端创建应用
            auto_create_app.delay(name, description, account_id)

            # 2.返回成功提示
            return f"已调用后端异步任务创建Agent应用。\n应用名称: {name}\n应用描述: {description}"

        create_app = SynchronizedStructuredTool.from_function(
            func=create_app,
            name="create_app",
            description="如果用户提出需要创建一个Agent/应用，你可以调用此工具，参数的输入是应用的名称+描述，返回的数据是创建后的成功提示",
            args_schema=CreateAppInput,
            return_direct=True,
        )
        return create_app

        # @tool("create_app", args_schema=CreateAppInput)
        # def create_app(name: str, description: str) -> str:
        #     """如果用户提出了需要创建一个Agent/应用，你可以调用此工具，参数的输入是应用的名称+描述，返回的数据是创建后的成功提示"""
        #     # 1.调用celery异步任务在后端创建应用
        #     auto_create_app.delay(name, description, account_id)
        #
        #     # 2.返回成功提示
        #     return f"已调用后端异步任务创建Agent应用。\n应用名称: {name}\n应用描述: {description}"
        #
        # return create_app

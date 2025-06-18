import json
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc
from typing_extensions import Any

from internal.exception import ValidateErrorException, NotFoundException
from internal.model import McpToolProvider, Account, McpTool
from internal.schema.mcp_api_schema import McpServersSchema
from internal.schema.mcp_schema import CreateMcpToolReq, UpdateMcpToolProviderReq, \
    GetMcpToolProvidersWithPageReq
from internal.task.mcp_tsak import handle_mcp_tool, update_mcp_tool
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .optimized_mcp_service import OptimizedMCPServiceWithFucCache


@inject
@dataclass
class McpService(BaseService):
    """mcp服务层"""
    db: SQLAlchemy
    optimized_mcp_service: OptimizedMCPServiceWithFucCache

    def parse_mcp_schema(self, mcp_schema_str: str):
        """解析传递的mcp_schema字符串，如果出错则抛出错误"""
        try:
            data = json.loads(mcp_schema_str.strip())
            if not isinstance(data, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("传递数据必须符合OpenAPI规范的JSON字符串")

        return McpServersSchema(**data)

    # def create_mcp_batch__tool(self, req: CreateMcpBatchToolReq, account: Account):
    #     """根据传递的请求创建自定义API工具"""
    #     # 1.检验并提取mcp_schema对应的数据
    #     mcp_schema = self.parse_mcp_schema(req.mcp_schema.data)
    #
    #     for server_name, server_config in mcp_schema.mcp_servers.items():
    #         real_mcp_schema = self.handle_mcp_schema(server_name, mcp_schema.mcp_servers.get(server_name))
    #
    #         mcp_tool_provider = self.db.session.query(McpToolProvider).filter_by(
    #             account_id=account.id,
    #             name=server_config.name
    #         ).one_or_none()
    #         if mcp_tool_provider is not None:
    #             raise ValidateErrorException(f"当前账号已经存在名为{server_config.name}的MCP工具提供者")
    #         with self.db.auto_commit():
    #             mcp_tool_provider = McpToolProvider(
    #                 account_id=account.id,
    #                 name=server_config.name,
    #                 icon=server_config.icon,
    #                 description=server_config.description,
    #                 mcp_schema=real_mcp_schema,
    #                 headers=server_config.headers
    #             )
    #             self.db.session.add(mcp_tool_provider)
    #             self.db.session.flush()
    #
    #             self.create(
    #                 McpTool,
    #                 account_id=account.id,
    #                 provider_id=mcp_tool_provider.id,
    #                 name=server_config.name,
    #                 description=server_config.description,
    #                 # TODO参数不确定，待完善
    #             )

    def handle_mcp_tool(self, account_id: UUID, mcp_provider_id: UUID, real_mcp_schema: dict):

        tools = self.optimized_mcp_service.get_langchain_tools_by_mcp_tool_config(real_mcp_schema)

        if tools is None:
            raise NotFoundException("未找到MCP工具")

        mcp_tools = self.db.session.query(McpTool).filter(
            McpTool.provider_id == mcp_provider_id,
            McpTool.account_id == account_id,
        ).all()
        if mcp_tools is not None:
            with self.db.auto_commit():
                self.db.session.query(McpTool).filter(
                    McpTool.provider_id == mcp_provider_id,
                    McpTool.account_id == account_id,
                ).delete()
                self.db.session.flush()

        for tool in tools:
            properties = tool.args_schema.get("properties")
            parameters = []
            for key, value in properties.items():
                parameters.append({
                    "in": "query",
                    "name": key,
                    "type": value.get("type"),
                    "required": True,
                    "description": value.get("description")
                })
            self.create(
                McpTool,
                account_id=account_id,
                provider_id=mcp_provider_id,
                name=tool.name,
                description=tool.description,
                args_schema=tool.args_schema,
                parameters=parameters,
            )

    def create_mcp_tool(self, req: CreateMcpToolReq, account: Account):
        # 1.检验并提取mcp_schema对应的数据
        mcp_schema = self.parse_mcp_schema(req.mcp_schema.data)

        server_name = list(mcp_schema.mcp_servers.keys())[0]
        real_mcp_schema = self.handle_mcp_schema(server_name, mcp_schema.mcp_servers.get(server_name))
        json_real_mcp_schema = json.dumps(real_mcp_schema)
        mcp_tool_provider = self.db.session.query(McpToolProvider).filter_by(
            account_id=account.id,
            name=req.name.data,
        ).one_or_none()
        if mcp_tool_provider is not None:
            raise ValidateErrorException(f"当前账号已经存在名为{req.name.data}的MCP工具提供者")
        with self.db.auto_commit():
            mcp_tool_provider = McpToolProvider(
                account_id=account.id,
                name=req.name.data,
                icon=req.icon.data,
                description=req.description.data,
                mcp_schema=json_real_mcp_schema,
                headers=req.headers.data
            )
            self.db.session.add(mcp_tool_provider)
            self.db.session.flush()

            # Clear existing tools for this provider (if updating existing)
            self.db.session.query(McpTool).filter_by(
                provider_id=mcp_tool_provider.id,
                account_id=account.id,
            ).delete()
            self.db.session.flush()

        handle_mcp_tool.delay(account.id, mcp_tool_provider.id, real_mcp_schema)

    def update_mcp_tool(self, account_id: UUID,
                        mcp_provider_id: UUID,
                        real_mcp_schema: dict,
                        ):

        tools = self.optimized_mcp_service.get_langchain_tools_by_mcp_tool_config(real_mcp_schema)

        if tools is None:
            raise NotFoundException("未找到MCP工具")

        mcp_tools = self.db.session.query(McpTool).filter(
            McpTool.provider_id == mcp_provider_id,
            McpTool.account_id == account_id,
        ).all()
        if mcp_tools is not None:
            with self.db.auto_commit():
                self.db.session.query(McpTool).filter(
                    McpTool.provider_id == mcp_provider_id,
                    McpTool.account_id == account_id,
                ).delete()
                self.db.session.flush()

        for tool in tools:
            properties = tool.args_schema.get("properties")
            parameters = []
            for key, value in properties.items():
                parameters.append({
                    "in": "query",
                    "name": key,
                    "type": value.get("type"),
                    "required": True,
                    "description": value.get("description")
                })

            self.create(
                McpTool,
                account_id=account_id,
                provider_id=mcp_provider_id,
                name=tool.name,
                description=tool.description,
                args_schema=tool.args_schema,
                parameters=parameters,
            )

            # [{"in": "query", "name": "q", "type": "str", "required": true, "description": "要检索查询的单词，例如love/computer"}, {"in": "query", "name": "doctype", "type": "str", "required": false, "description": "返回的数据类型，支持json和xml两种格式，默认情况下json数据"}]
            # {"city": {"type": "string", "description": "公共交通规划起点城市"}, "cityd": {"type": "string", "description": "公共交通规划终点城市"}, "origin": {"type": "string", "description": "出发点经度，纬度，坐标格式为：经度，纬度"}, "destination": {"type": "string", "description": "目的地经度，纬度，坐标格式为：经度，纬度"}}

    def update_mcp_tool_provider(self, provider_id: UUID, req: UpdateMcpToolProviderReq, account: Account):
        mcp_tool_provider = self.get(McpToolProvider, provider_id)
        if not mcp_tool_provider or mcp_tool_provider.account_id != account.id:
            raise ValidateErrorException("当前用户没有权限修改该MCP工具提供者")

        mcp_schema = self.parse_mcp_schema(req.mcp_schema.data)

        server_name = list(mcp_schema.mcp_servers.keys())[0]
        real_mcp_schema = self.handle_mcp_schema(server_name, mcp_schema.mcp_servers.get(server_name))
        json_real_mcp_schema = json.dumps(real_mcp_schema)

        check_mcp_tool_provider = self.db.session.query(McpToolProvider).filter(
            McpToolProvider.account_id == account.id,
            McpToolProvider.name == req.name.data,
            McpToolProvider.id != mcp_tool_provider.id,

        ).one_or_none()
        if check_mcp_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name.data}已存在")
        # 4.开启数据库的自动提交
        with self.db.auto_commit():
            self.db.session.query(McpTool).filter(
                McpTool.provider_id == mcp_tool_provider.id,
                McpTool.account_id == account.id,
            ).delete()
            self.db.session.flush()

            self.update(
                mcp_tool_provider,
                name=req.name.data,
                icon=req.icon.data,
                description=req.description.data,
                mcp_schema=json_real_mcp_schema,
                headers=req.headers.data

            )

        update_mcp_tool.delay(account.id, mcp_tool_provider.id, real_mcp_schema)

    def get_mcp_tool(self, provider_id, tool_name, current_user):
        mcp_tool = self.db.session.query(McpTool).filter_by(
            provider_id=provider_id,
            name=tool_name,
        ).one_or_none()
        if mcp_tool is None or mcp_tool.account_id != current_user.id:
            raise NotFoundException("该工具不存在")

        return mcp_tool

    def get_mcp_tool_provider(self, provider_id, current_user):
        mcp_tool_provider = self.get(
            McpToolProvider,
            provider_id
        )
        if mcp_tool_provider is None or mcp_tool_provider.account_id != current_user.id:
            raise NotFoundException("该工具提供者不存在")
        return mcp_tool_provider

    def delete_api_tool_provider(self, provider_id, current_user):
        mcp_tool_provider = self.get(McpToolProvider, provider_id)

        if mcp_tool_provider is None or mcp_tool_provider.account_id != current_user.id:
            raise NotFoundException("该工具提供者不存在")
        with self.db.auto_commit():
            self.db.session.query(McpTool).filter(
                McpTool.provider_id == provider_id,
                McpTool.account_id == current_user.id

            ).delete()

            self.db.session.delete(mcp_tool_provider)

    def get_mcp_tool_providers_with_page(
            self,
            req: GetMcpToolProvidersWithPageReq,
            account: Account,
    ) -> tuple[list[Any], Paginator]:
        """获取自定义API工具服务提供者分页列表数据"""
        # 1.构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 2.构建筛选器
        filters = [McpToolProvider.account_id == account.id]
        if req.search_word.data:
            filters.append(McpToolProvider.name.ilike(f"%{req.search_word.data}%"))

        # 3.执行分页并获取数据
        mcp_tool_providers = paginator.paginate(
            self.db.session.query(McpToolProvider).filter(*filters).order_by(desc("created_at"))
        )

        return mcp_tool_providers, paginator

    def get_mcp_tool_by_provider_ids(self, provider_ids: list[UUID]):
        mcp_providers: list[McpToolProvider] = self.db.session.query(McpToolProvider).filter(
            McpToolProvider.id.in_(provider_ids)
        ).all()
        if mcp_providers is None:
            raise NotFoundException("提供的mcp提供者列表为空")
        total_mcp_schema = {}
        for mcp_provider in mcp_providers:
            mcp_schema = json.loads(mcp_provider.mcp_schema)
            mcp_schema = mcp_schema.get("mcpServers")
            for server_name, sever_config in mcp_schema.items():
                target_server_config = {
                    "command": sever_config.get("command"),
                    "args": sever_config.get("args"),
                    "env": sever_config.get("env"),
                    "transport": sever_config.get("transport"),
                }
                total_mcp_schema[server_name] = target_server_config
        tools = self.optimized_mcp_service.get_langchain_tools_by_mcp_tool_config(total_mcp_schema)
        return tools

    @classmethod
    def handle_mcp_schema(cls, mcp_server_name: str, server_config):
        json_schema = (
            {
                "mcpServers": {
                    mcp_server_name: {
                        "command": server_config.command,
                        "args": server_config.args,
                        "env": server_config.env,
                        "transport": server_config.transport,
                    }
                }
            }

        )

        return json_schema

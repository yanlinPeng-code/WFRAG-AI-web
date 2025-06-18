from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject

from internal.schema.mcp_schema import ValidateMcpSchemaReq, CreateMcpToolReq, UpdateMcpToolProviderReq, GetMcpToolResp, \
    GetMcpToolProviderResp, GetMcpToolProvidersWithPageReq, \
    GetMcpToolProvidersWithPageResp
from internal.service import McpService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_message, success_json


@inject
@dataclass
class McpHandler:
    """MCP处理器"""
    mcp_service: McpService

    @login_required
    def validate_mcp_schema(self):
        """校验传递的openapi_schema字符串是否正确"""
        req = ValidateMcpSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

        schema = self.mcp_service.parse_mcp_schema(req.mcp_schema.data)
        return success_message("数据校验成功")

    # @login_required
    # def create_mcp_tool_batch_provider(self):
    #     """创建自定义API工具"""
    #     req = CreateMcpBatchToolReq()
    #     if not req.validate():
    #         return validate_error_json(req.errors)
    #
    #     self.mcp_service.create_mcp_batch__tool(req, current_user)
    #
    #     return success_message("创建自定义MCP工具插件成功")

    @login_required
    def create_mcp_tool_provider(self):
        """创建自定义API工具"""
        req = CreateMcpToolReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.mcp_service.create_mcp_tool(req, current_user)

        return success_message("创建自定义MCP工具插件成功")

    @login_required
    def update_mcp_tool_provider(self, provider_id: UUID):
        """更新自定义API工具提供者信息"""
        req = UpdateMcpToolProviderReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.mcp_service.update_mcp_tool_provider(provider_id, req, current_user)

        return success_message("更新mcp插件成功")

    @login_required
    def get_mcp_tool(self, provider_id: UUID, tool_name: str):
        """根据传递的provider_id+tool_name获取工具的详情信息"""
        api_tool = self.mcp_service.get_mcp_tool(provider_id, tool_name, current_user)

        resp = GetMcpToolResp()

        return success_json(resp.dump(api_tool))

    @login_required
    def get_mcp_tool_provider(self, provider_id: UUID):
        """根据传递的provider_id获取工具提供者的原始信息"""
        api_tool_provider = self.mcp_service.get_mcp_tool_provider(provider_id, current_user)

        resp = GetMcpToolProviderResp()

        return success_json(resp.dump(api_tool_provider))

    #
    @login_required
    def delete_mcp_tool_provider(self, provider_id: UUID):
        """根据传递的provider_id删除对应的工具提供者信息"""
        self.mcp_service.delete_api_tool_provider(provider_id, current_user)

        return success_message("删除自定义mcp插件成功")

    @login_required
    def get_mcp_tool_providers_with_page(self):
        req = GetMcpToolProvidersWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        mcp_tool_providers, paginator = self.mcp_service.get_mcp_tool_providers_with_page(req, current_user)

        resp = GetMcpToolProvidersWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(mcp_tool_providers), paginator=paginator))

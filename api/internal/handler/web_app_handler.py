from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject

from internal.schema.web_app_schema import WebAppChatReq, GetConversationsReq, GetConversationsResp
from internal.service import WebAppService
from pkg.response import validate_error_json, compact_generate_response, success_json, success_message


@inject
@dataclass
class WebAppHandler:
    """WebApp处理器"""
    web_app_service: WebAppService

    @login_required
    def get_web_app(self, token: str):
        """根据传递的token凭证标识获取WebApp基础信息"""
        # 1.调用服务根据传递的token获取应用信息（添加features模型特性）
        resp = self.web_app_service.get_web_app_info(token)

        # 2.返回成功响应
        return success_json(resp)

    @login_required
    def web_app_chat(self, token: str):
        """根据传递的token+query等信息与WebApp进行对话"""
        # 1.提取请求并校验
        req = WebAppChatReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务获取对应响应内容
        response = self.web_app_service.web_app_chat(token, req, current_user)

        return compact_generate_response(response)

    @login_required
    def stop_web_app_chat(self, token: str, task_id: UUID):
        """根据传递的token+task_id停止与WebApp的对话"""
        self.web_app_service.stop_web_app_chat(token, task_id, current_user)
        return success_message("停止WebApp会话成功")

    @login_required
    def get_conversations(self, token: str):
        """根据传递的token+is_pinned获取指定WebApp下的所有会话列表信息"""
        # 1.提取请求并校验
        req = GetConversationsReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务获取会话列表
        conversations = self.web_app_service.get_conversations(token, req.is_pinned.data, current_user)

        # 3.构建响应并返回
        resp = GetConversationsResp(many=True)

        return success_json(resp.dump(conversations))

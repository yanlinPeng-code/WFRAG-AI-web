from dataclasses import dataclass

from injector import inject

from internal.schema.oauth_schema import AuthorizeReq, AuthorizeResp
from internal.service import OAuthService
from pkg.response import success_json, validate_error_json


@inject
@dataclass
class OAuthHandler:
    """第三方授权认证信息"""
    oauth_service: OAuthService

    def provider(self, provider_name: str):
        """根据传递的提供商名字获取授权认证重定向地址"""
        # 1.根据provider_name获取授权服务提供商
        oauth = self.oauth_service.get_oauth_by_provider_name(provider_name)

        redirect_url = oauth.get_authorization_url()

        return success_json({"redirect_url": redirect_url})

    def authorize(self, provider_name: str):
        """根据传递的提供商名字获取授权认证信息+code获取第三方授权信息"""
        req = AuthorizeReq()
        if not req:
            return validate_error_json(req.errors)
        credential = self.oauth_service.oauth_login(provider_name, req.code.data)

        return success_json(AuthorizeResp().dump(credential))

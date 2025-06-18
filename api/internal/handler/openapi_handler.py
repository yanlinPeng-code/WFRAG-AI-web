from dataclasses import dataclass

from flask_login import current_user, login_required
from injector import inject

from internal.schema.openapi_schema import OpenAPIChatReq
from internal.service import OpenAPIService
from pkg.response import validate_error_json, compact_generate_response


@inject
@dataclass
class OpenApiHandler:
    openapi_service: OpenAPIService

    @login_required
    def chat(self):
        """开放Chat对话接口"""
        req = OpenAPIChatReq()
        if not req.validate():
            return validate_error_json(req.errors)
        resp = self.openapi_service.chat(req, current_user)
        return compact_generate_response(resp)

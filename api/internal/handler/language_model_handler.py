import io
from dataclasses import dataclass

from flask import send_file
from injector import inject

from internal.service import LanguageModelService
from pkg.response import success_json


@inject
@dataclass
class LanguageModelHandler:
    """语言模型处理器"""
    language_model_service: LanguageModelService

    def get_language_models(self):
        """获取所有语言模型提供商的信息"""
        return success_json(self.language_model_service.get_language_models())

    def get_language_model(self, provider_name: str, model_name: str):
        return success_json(self.language_model_service.get_language_model(provider_name, model_name))

    def get_language_model_icon(self, provider_name: str):
        icon, mimetype = self.language_model_service.get_language_model_icon(provider_name)
        return send_file(io.BytesIO(icon), mimetype)

import os

import tiktoken
from langchain_openai import ChatOpenAI
from typing_extensions import Tuple

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """通义千问聊天模型"""

    def __init__(self, *args, **kwargs):  # 添加 model_name 参数
        # 默认从环境变量获取 API 密钥和基础 URL
        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("DASHSCOPE_BASE_URL")

        # # 根据模型名称设置 streaming
        # if model_name == "qwen-omni-turbo":
        #     kwargs["streaming"] = True  # 设置 streaming 为 True
        # else:
        #     # 对于其他模型，可以根据需要设置 streaming，或者保持默认行为
        #     # ChatOpenAI 默认 streaming=False
        #     pass

        # 调用父类的 __init__ 方法，传入所有参数
        super().__init__(*args, api_key=api_key, base_url=base_url, **kwargs)

    def _get_encoding_model(self) -> Tuple[str, tiktoken.Encoding]:
        """重写月之暗面获取编码模型名字+模型函数，该类继承OpenAI，词表模型可以使用gpt-3.5-turbo防止出错"""
        # 1.将DeepSeek的词表模型设置为gpt-3.5-turbo
        model = "gpt-3.5-turbo"

        # 2.返回模型名字+编码器
        return model, tiktoken.encoding_for_model(model)

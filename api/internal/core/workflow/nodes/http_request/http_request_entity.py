from enum import Enum

from pydantic import Field, HttpUrl, field_validator
from typing_extensions import Optional

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.vailate_entity import VariableEntity, VariableType, VariableValueType
from internal.exception import ValidateErrorException


#
# class HttpRequestMethod(str, Enum):
#     """Http请求方法类型枚举"""
#     GET = "get"
#     POST = "post"
#     PUT = "put"
#     PATCH = "patch"
#     DELETE = "delete"
#     HEAD = "head"
#     OPTIONS = "options"
#
#
# class HttpRequestInputType(str, Enum):
#     """Http请求输入变量类型"""
#     PARAMS = "params"  # query参数
#     HEADERS = "headers"  # header请求头
#     BODY = "body"  # body参数
#
#
# class HttpRequestNodeData(BaseNodeData):
#     """http请求节点"""
#     url: Optional[HttpUrl] = None
#     method: HttpRequestMethod = HttpRequestMethod.GET
#
#     inputs: list[VariableEntity] = Field(default_factory=list)
#     outputs: list[VariableEntity] = Field(
#         default_factory=lambda: [
#             VariableEntity(
#                 name="status_code",
#                 type=VariableType.INT,
#                 value={"type": VariableValueType.GENERATED, "content": 0},
#             ),
#             VariableEntity(name="text", value={"type": VariableValueType.GENERATED}),
#         ],
#     )
#
#     @classmethod
#     @field_validator("url", mode="before")
#     def validate_url(cls, url: Optional[HttpUrl]):
#         return url if url != " " else None
#         # 添加model_serializer来处理URL的序列化
#
#     def model_dump(self, **kwargs):
#         data = super().model_dump(**kwargs)
#         # 如果URL存在，将其转换为字符串
#         if data.get("url") is not None:
#             data["url"] = str(data["url"])
#         return data
#
#     @classmethod
#     @field_validator("outputs", mode="before")
#     def validate_outputs(cls, outputs: list[VariableEntity]):
#         return [
#             VariableEntity(
#                 name="status_code",
#                 type=VariableType.INT,
#                 value={"type": VariableValueType.GENERATED, "content": 0},
#             ),
#             VariableEntity(name="text", value={"type": VariableValueType.GENERATED}),
#         ]
#
#     @classmethod
#     @field_validator("inputs")
#     def validate_inputs(cls, inputs: list[VariableEntity]):
#         for input in inputs:
#             if input.meta.get("type") not in HttpRequestInputType.__members__.values():
#                 raise ValueError(f"{input.meta.get('type')} is not a valid input type")
#         return inputs
class HttpRequestMethod(str, Enum):
    """Http请求方法类型枚举"""
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"


class HttpRequestInputType(str, Enum):
    """Http请求输入变量类型"""
    PARAMS = "params"  # query参数
    HEADERS = "headers"  # header请求头
    BODY = "body"  # body参数


class HttpRequestNodeData(BaseNodeData):
    """HTTP请求节点数据"""
    url: Optional[HttpUrl] = None  # 请求URL地址
    method: HttpRequestMethod = HttpRequestMethod.GET  # API请求方法
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入变量列表
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(
                name="status_code",
                type=VariableType.INT,
                value={"type": VariableValueType.GENERATED, "content": 0},
            ),
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED}),
        ],
    )

    @field_validator("url", mode="before")
    def validate_url(cls, url: Optional[HttpUrl]):
        return url if url != "" else None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # 如果URL存在，将其转换为字符串
        if data.get("url") is not None:
            data["url"] = str(data["url"])
        return data

    @field_validator("outputs", mode="before")
    def validate_outputs(cls, outputs: list[VariableEntity]):
        return [
            VariableEntity(
                name="status_code",
                type=VariableType.INT,
                value={"type": VariableValueType.GENERATED, "content": 0},
            ),
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED}),
        ]

    @field_validator("inputs")
    def validate_inputs(cls, inputs: list[VariableEntity]):
        """校验输入列表数据"""
        # 1.校验判断输入变量列表中的类型信息
        for input in inputs:
            if input.meta.get("type") not in HttpRequestInputType.__members__.values():
                raise ValidateErrorException("Http请求参数结构出错")

        # 2.返回校验后的数据
        return inputs

import json
from typing import Dict, List, Any, Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


class McpServerConfig(BaseModel):
    """单个MCP服务器配置模型"""
    model_config = ConfigDict(
        # 允许序列化时使用别名
        populate_by_name=True,
        # 验证赋值
        validate_assignment=True
    )

    # 修正：使用Optional[str]而不是Field(Optional[str])
    description: Optional[str] = Field(default=None, description="服务器描述")
    icon: Optional[str] = Field(default=None, description="服务器图标")
    name: Optional[str] = Field(default=None, description="服务器名称")
    headers: List[Union[str, Dict[str, Any]]] = Field(default_factory=list, alias="hearders", description="请求头配置")
    command: str = Field(..., description="执行命令")
    args: List[str] = Field(..., description="命令参数列表")
    env: Optional[Dict[str, str]] = Field(default=None, description="环境变量配置")
    transport: str = Field(..., description="传输方式")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        # 如果是None，直接返回
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("description必须是字符串类型")

        # 去除空格后检查是否为空
        stripped = v.strip()
        if not stripped:
            raise ValueError("description不能为空字符串")

        return stripped

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        # 如果是None，直接返回
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("icon必须是字符串类型")

        # 去除空格后检查是否为空
        stripped = v.strip()
        if not stripped:
            raise ValueError("icon不能为空字符串")

        return stripped

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        # 如果是None，直接返回
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("name必须是字符串类型")

        # 去除空格后检查是否为空
        stripped = v.strip()
        if not stripped:
            raise ValueError("name不能为空字符串")

        return stripped

    @field_validator("headers", mode="before")
    @classmethod
    def validate_headers(cls, v: Any) -> List[Union[str, Dict[str, Any]]]:
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("headers必须是列表类型")

        # 验证列表中的每个元素
        validated_headers = []
        for i, header in enumerate(v):
            if isinstance(header, str):
                validated_headers.append(header)
            elif isinstance(header, dict):
                validated_headers.append(header)
            else:
                raise ValueError(f"headers[{i}]必须是字符串或字典类型")

        return validated_headers

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("command必须是字符串类型")

        stripped = v.strip()
        if not stripped:
            raise ValueError("command不能为空")

        # 先检查类型和空值，再检查具体值
        keys = {"npx", "npm", "uv"}
        if stripped not in keys:
            raise ValueError("command必须是npx、npm、uv中的一种")

        return stripped

    @field_validator("args")
    @classmethod
    def validate_args(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("args必须是列表类型")
        if len(v) == 0:
            raise ValueError("args不能为空列表")

        # 验证每个参数都是字符串
        validated_args = []
        for i, arg in enumerate(v):
            if not isinstance(arg, str):
                raise ValueError(f"args[{i}]必须是字符串类型")
            validated_args.append(arg)

        return validated_args

    @field_validator("env")
    @classmethod
    def validate_env(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("env必须是字典类型")

        # 验证所有键值对都是字符串
        validated_env = {}
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError("env中的键必须是字符串类型")
            if not isinstance(value, str):
                raise ValueError(f"env中键'{key}'的值必须是字符串类型")
            validated_env[key] = value

        return validated_env

    @field_validator("transport")
    @classmethod
    def validate_transport(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("transport必须是字符串类型")

        stripped = v.strip()
        if not stripped:
            raise ValueError("transport不能为空")

        # 修正：错误信息应该与验证逻辑一致
        if stripped not in ["stdio", "sse"]:
            raise ValueError("transport必须是stdio或sse")

        return stripped


class McpServersSchema(BaseModel):
    """MCP服务器配置主模型"""
    model_config = ConfigDict(
        # 允许序列化时使用别名
        populate_by_name=True,
        # 验证赋值
        validate_assignment=True
    )

    mcp_servers: Dict[str, McpServerConfig] = Field(
        default_factory=dict,
        alias="mcpServers",
        description="MCP服务器配置字典"
    )

    @field_validator("mcp_servers", mode="before")
    @classmethod
    def validate_mcp_servers(cls, v: Any) -> Dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("mcpServers必须是字典类型")

        if len(v) == 0:
            raise ValueError("mcpServers不能为空字典")

        # 验证每个服务器配置
        for server_name, server_config in v.items():
            if not isinstance(server_name, str):
                raise ValueError("服务器名称必须是字符串类型")

            if not isinstance(server_config, dict):
                raise ValueError(f"服务器 '{server_name}' 的配置必须是字典类型")

            # 修正：由于字段现在是可选的，只检查必需字段
            required_fields = ["command", "args", "transport"]
            for field in required_fields:
                if field not in server_config:
                    raise ValueError(f"服务器 '{server_name}' 缺少必需字段: {field}")

        return v

    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化的字典"""
        return self.model_dump(by_alias=True)

    def to_json(self, indent: Optional[int] = None) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

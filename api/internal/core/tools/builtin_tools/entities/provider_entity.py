#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/19 17:13
@Author  : thezehui@gmail.com
@File    : provider_entity.py
"""
import os.path
from typing_extensions import Any

import yaml
from pydantic import BaseModel, Field

from internal.lib.helper import dynamic_import
from .tool_entity import ToolEntity


class ProviderEntity(BaseModel):
    """服务提供商实体，映射的数据是providers.yaml里的每条记录"""
    name: str  # 名字
    label: str  # 标签、展示给前端显示的
    description: str  # 描述
    icon: str  # 图标地址
    background: str  # 图标的颜色
    category: str  # 分类信息
    created_at: int = 0  # 提供商/工具的创建时间戳


class Provider(BaseModel):
    """服务提供商，在该类下，可以获取到该服务提供商的所有工具、描述、图标等多个信息"""
    name: str  # 服务提供商的名字
    position: int  # 服务提供商的顺序
    provider_entity: ProviderEntity  # 服务提供商实体
    tool_entity_map: dict[str, ToolEntity] = Field(default_factory=dict)  # 工具实体映射表
    tool_func_map: dict[str, Any] = Field(default_factory=dict)  # 工具函数映射表

    def __init__(self, **kwargs):
        """构造函数，完成对应服务提供商的初始化"""
        super().__init__(**kwargs)
        self._provider_init()

    def get_tool(self, tool_name: str) -> Any:
        """根据工具的名字，来获取到该服务提供商下的指定工具"""
        return self.tool_func_map.get(tool_name)

    def get_tool_entity(self, tool_name: str) -> ToolEntity:
        """根据工具的名字，来获取到该服务提供商下的指定工具的实体/信息"""
        return self.tool_entity_map.get(tool_name)

    def get_tool_entities(self) -> list[ToolEntity]:
        """获取该服务提供商下的所有工具实体/信息列表"""
        return list(self.tool_entity_map.values())

    def _provider_init(self):
        """服务提供商初始化函数"""
        # 1.获取当前类的路径，计算的到对应服务提供商的地址/路径
        current_path = os.path.abspath(__file__)
        entities_path = os.path.dirname(current_path)
        provider_path = os.path.join(os.path.dirname(entities_path), "providers", self.name)

        # 2.组装获取positions.yaml数据
        positions_yaml_path = os.path.join(provider_path, "positions.yaml")
        with open(positions_yaml_path, encoding="utf-8") as f:
            positions_yaml_data = yaml.safe_load(f)

        # 3.循环读取位置信息获取服务提供商的工具名字
        for tool_name in positions_yaml_data:
            # 4.获取工具的yaml数据
            tool_yaml_path = os.path.join(provider_path, f"{tool_name}.yaml")
            with open(tool_yaml_path, encoding="utf-8") as f:
                tool_yaml_data = yaml.safe_load(f)

            # 5.将工具信息实体赋值填充到tool_entity_map中
            self.tool_entity_map[tool_name] = ToolEntity(**tool_yaml_data)

            # 6.动态导入对应的工具并填充到tool_func_map中
            self.tool_func_map[tool_name] = dynamic_import(
                f"internal.core.tools.builtin_tools.providers.{self.name}",
                tool_name,
            )

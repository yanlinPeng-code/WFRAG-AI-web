from pydantic import field_validator, Field
from typing_extensions import List

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.vailate_entity import VariableEntity, VariableValueType


class SqlSearchNodeData(BaseNodeData):
    """SQL查询节点数据，只允许执行SELECT语句，前端需选择表名"""
    inputs: List[VariableEntity] = Field(default_factory=list)
    outputs: List[VariableEntity] = Field(default_factory=lambda: [
        VariableEntity(name="text", value={"type": VariableValueType.GENERATED})
    ])

    @field_validator("inputs")
    def validate_inputs(cls, value: List[VariableEntity]):
        required_names = {"host", "port", "user", "password", "database", "table"}
        input_names = {i.name for i in value}
        missing = required_names - input_names
        if missing:
            raise ValueError(f"sql_search节点缺少必要输入: {', '.join(missing)}")

        # 验证每个字段的值类型
        for var in value:
            if var.name in {"host", "port", "user", "password", "database", "table"}:
                # 数据库连接参数和表名必须是LITERAL类型（直接输入）
                if var.value.type != VariableValueType.LITERAL:
                    raise ValueError(f"数据库连接参数或表名 '{var.name}' 必须是直接输入类型")
           
        return value

    @field_validator("outputs", mode="before")
    def validate_outputs(cls, v):
        return [
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED})
        ]

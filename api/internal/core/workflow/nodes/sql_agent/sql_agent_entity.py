from pydantic import field_validator, Field
from typing_extensions import List, Any

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.vailate_entity import VariableEntity, VariableValueType
from internal.entity.app_entity import DEFAULT_APP_CONFIG


class SqlAgentNodeData(BaseNodeData):
    """SQL智能代理节点数据，自动生成SQL并执行"""
    prompt: str
    language_model_config: dict[str, Any] = Field(
        alias="model_config",
        default_factory=lambda: DEFAULT_APP_CONFIG["model_config"]
    )
    inputs: List[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
        ]
    )

    @field_validator("inputs")
    def validate_inputs(cls, value: list[VariableEntity]):
        required_names = {"host", "port", "user", "password", "database"}
        input_names = {i.name for i in value}
        missing = required_names - input_names
        if missing:
            raise ValueError(f"sql_agent节点缺少必要输入: {', '.join(missing)}")

        # 验证每个字段的值类型
        for var in value:
            if var.name in {"host", "port", "user", "password", "database"}:
                # 数据库连接参数必须是LITERAL类型（直接输入）
                if var.value.type != VariableValueType.LITERAL:
                    raise ValueError(f"数据库连接参数 '{var.name}' 必须是直接输入类型")
            # elif var.name == "query":
            #     # query字段可以是LITERAL或REF类型
            #     if var.value.type not in {VariableValueType.LITERAL, VariableValueType.REF}:
            #         raise ValueError(f"查询参数 'query' 必须是直接输入或引用类型")
            #
            #     # 如果是REF类型，检查引用内容是否完整
            #     if var.value.type == VariableValueType.REF:
            #         if isinstance(var.value.content, VariableEntity.Value.Content):
            #             if not var.value.content.ref_node_id or not var.value.content.ref_var_name:
            #                 raise ValueError("query字段引用类型时，必须指定引用节点ID和变量名")
            #         else:
            #             raise ValueError("query字段引用类型时，content必须是Content类型")

        return value

    @field_validator("outputs", mode="before")
    def validate_outputs(cls, value: list[VariableEntity]):
        return [
            VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
        ]

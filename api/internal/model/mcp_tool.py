from datetime import datetime

from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    DateTime,
    text,
    PrimaryKeyConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB

from internal.extension.database_extension import db


class McpToolProvider(db.Model):
    """API工具提供者模型"""
    __tablename__ = "mcp_tool_provider"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_mcp_tool_provider_id"),
        Index("mcp_tool_provider_account_id_idx", "account_id"),
        Index("mcp_tool_name_idx", "name"),
    )

    id = Column(UUID, nullable=False, server_default=text('uuid_generate_v4()'))
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    icon = Column(String(255), nullable=False, server_default=text("''::character varying"))
    description = Column(Text, nullable=False, server_default=text("''::text"))
    mcp_schema = Column(Text, nullable=False, server_default=text("''::text"))
    headers = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        onupdate=datetime.now,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def tools(self) -> list["McpTool"]:
        return db.session.query(McpTool).filter_by(provider_id=self.id).all()


class McpTool(db.Model):
    """API工具表"""
    __tablename__ = "mcp_tool"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_mcp_tool_id"),
        Index("mcp_tool_account_id_idx", "account_id"),
        Index("mcp_tool_provider_id_name_idx", "provider_id", "name"),
    )

    id = Column(UUID, nullable=False, server_default=text('uuid_generate_v4()'))
    account_id = Column(UUID, nullable=False)
    provider_id = Column(UUID, nullable=False)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    description = Column(Text, nullable=False, server_default=text("''::text"))
    args_schema = Column(JSONB, nullable=True, server_default=text("'[]'::jsonb"))
    parameters = Column(JSONB, nullable=True, server_default=text("'[]'::jsonb"))
    tool_list = Column(JSONB, nullable=True, server_default=text("'[]'::jsonb"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        onupdate=datetime.now,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def provider(self) -> "McpToolProvider":
        """只读属性，返回当前工具关联/归属的工具提供者信息"""
        return db.session.query(McpToolProvider).get(self.provider_id)

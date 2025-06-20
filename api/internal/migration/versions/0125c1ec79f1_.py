"""empty message

Revision ID: 0125c1ec79f1
Revises: 5adb2d84dfc8
Create Date: 2025-05-27 14:21:48.847433

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0125c1ec79f1'
down_revision = '5adb2d84dfc8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mcp_tool',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('provider_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('description', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('url', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=True),
    sa.Column('method', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=True),
    sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_mcp_tool_id')
    )
    with op.batch_alter_table('mcp_tool', schema=None) as batch_op:
        batch_op.create_index('mcp_tool_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('mcp_tool_provider_id_name_idx', ['provider_id', 'name'], unique=False)

    op.create_table('mcp_tool_provider',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('icon', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('description', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('mcp_schema', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('headers', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_mcp_tool_provider_id')
    )
    with op.batch_alter_table('mcp_tool_provider', schema=None) as batch_op:
        batch_op.create_index('mcp_tool_name_idx', ['name'], unique=False)
        batch_op.create_index('mcp_tool_provider_account_id_idx', ['account_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mcp_tool_provider', schema=None) as batch_op:
        batch_op.drop_index('mcp_tool_provider_account_id_idx')
        batch_op.drop_index('mcp_tool_name_idx')

    op.drop_table('mcp_tool_provider')
    with op.batch_alter_table('mcp_tool', schema=None) as batch_op:
        batch_op.drop_index('mcp_tool_provider_id_name_idx')
        batch_op.drop_index('mcp_tool_account_id_idx')

    op.drop_table('mcp_tool')
    # ### end Alembic commands ###

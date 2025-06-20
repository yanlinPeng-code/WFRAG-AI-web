"""empty message

Revision ID: eb4cee7ef581
Revises: 826531831354
Create Date: 2025-05-10 18:06:25.980842

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'eb4cee7ef581'
down_revision = '826531831354'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_config',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('app_id', sa.UUID(), nullable=False),
    sa.Column('model_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('dialog_round', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('preset_prompt', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('tools', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('workflows', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('retrieval_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('long_term_memory', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('opening_statement', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('opening_questions', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('speech_to_text', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('text_to_speech', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('suggested_after_answer', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text('\'{"enable": true}\'::jsonb'), nullable=False),
    sa.Column('review_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_id')
    )
    with op.batch_alter_table('app_config', schema=None) as batch_op:
        batch_op.create_index('app_config_app_id_idx', ['app_id'], unique=False)

    op.create_table('app_config_version',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('app_id', sa.UUID(), nullable=False),
    sa.Column('model_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('dialog_round', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('preset_prompt', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('tools', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('workflows', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('datasets', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('retrieval_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('long_term_memory', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('opening_statement', sa.Text(), server_default=sa.text("''::text"), nullable=False),
    sa.Column('opening_questions', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('speech_to_text', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('text_to_speech', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('suggested_after_answer', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text('\'{"enable": true}\'::jsonb'), nullable=False),
    sa.Column('review_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('version', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('config_type', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_version_id')
    )
    with op.batch_alter_table('app_config_version', schema=None) as batch_op:
        batch_op.create_index('app_config_version_app_id_idx', ['app_id'], unique=False)

    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assistant_agent_conversation_id', sa.UUID(), nullable=True))
        batch_op.create_index('account_email_idx', ['email'], unique=False)

    with op.batch_alter_table('account_oauth', schema=None) as batch_op:
        batch_op.create_index('account_oauth_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('account_oauth_openid_provider_idx', ['openid', 'provider'], unique=False)

    with op.batch_alter_table('api_tool', schema=None) as batch_op:
        batch_op.create_index('api_tool_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('api_tool_provider_id_name_idx', ['provider_id', 'name'], unique=False)

    with op.batch_alter_table('api_tool_provider', schema=None) as batch_op:
        batch_op.create_index('api_tool_name_idx', ['name'], unique=False)
        batch_op.create_index('api_tool_provider_account_id_idx', ['account_id'], unique=False)

    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.add_column(sa.Column('app_config_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('draft_app_config_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('debug_conversation_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('token', sa.String(length=255), server_default=sa.text("''::character varying"), nullable=True))
        batch_op.alter_column('account_id',
               existing_type=sa.UUID(),
               nullable=False)
        batch_op.drop_index('idx_app_account_id')
        batch_op.create_index('app_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('app_token_idx', ['token'], unique=False)

    with op.batch_alter_table('app_dataset_join', schema=None) as batch_op:
        batch_op.create_index('app_dataset_join_app_id_dataset_id_idx', ['app_id', 'dataset_id'], unique=False)

    with op.batch_alter_table('conversation', schema=None) as batch_op:
        batch_op.create_index('conversation_app_created_by_idx', ['created_by'], unique=False)
        batch_op.create_index('conversation_app_id_idx', ['app_id'], unique=False)

    with op.batch_alter_table('dataset', schema=None) as batch_op:
        batch_op.create_index('dataset_account_id_name_idx', ['account_id', 'name'], unique=False)

    with op.batch_alter_table('dataset_query', schema=None) as batch_op:
        batch_op.create_index('dataset_created_by_idx', ['created_by'], unique=False)
        batch_op.create_index('dataset_query_dataset_id_idx', ['dataset_id'], unique=False)
        batch_op.create_index('dataset_source_app_id_idx', ['source_app_id'], unique=False)

    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.create_index('document_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('document_batch_idx', ['batch'], unique=False)
        batch_op.create_index('document_dataset_id_idx', ['dataset_id'], unique=False)

    with op.batch_alter_table('keyword_table', schema=None) as batch_op:
        batch_op.create_index('keyword_table_dataset_id_idx', ['dataset_id'], unique=False)

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_urls', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False))
        batch_op.create_index('message_conversation_id_idx', ['conversation_id'], unique=False)
        batch_op.create_index('message_created_by_idx', ['created_by'], unique=False)

    with op.batch_alter_table('message_agent_thought', schema=None) as batch_op:
        batch_op.create_index('message_agent_thought_app_id_idx', ['app_id'], unique=False)
        batch_op.create_index('message_agent_thought_conversation_id_idx', ['conversation_id'], unique=False)
        batch_op.create_index('message_agent_thought_message_id_idx', ['message_id'], unique=False)

    with op.batch_alter_table('process_rule', schema=None) as batch_op:
        batch_op.create_index('process_rule_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('process_rule_dataset_id_idx', ['dataset_id'], unique=False)

    with op.batch_alter_table('segment', schema=None) as batch_op:
        batch_op.create_index('segment_account_id_idx', ['account_id'], unique=False)
        batch_op.create_index('segment_dataset_id_idx', ['dataset_id'], unique=False)
        batch_op.create_index('segment_document_id_idx', ['document_id'], unique=False)

    with op.batch_alter_table('upload_file', schema=None) as batch_op:
        batch_op.create_index('upload_file_account_id_idx', ['account_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('upload_file', schema=None) as batch_op:
        batch_op.drop_index('upload_file_account_id_idx')

    with op.batch_alter_table('segment', schema=None) as batch_op:
        batch_op.drop_index('segment_document_id_idx')
        batch_op.drop_index('segment_dataset_id_idx')
        batch_op.drop_index('segment_account_id_idx')

    with op.batch_alter_table('process_rule', schema=None) as batch_op:
        batch_op.drop_index('process_rule_dataset_id_idx')
        batch_op.drop_index('process_rule_account_id_idx')

    with op.batch_alter_table('message_agent_thought', schema=None) as batch_op:
        batch_op.drop_index('message_agent_thought_message_id_idx')
        batch_op.drop_index('message_agent_thought_conversation_id_idx')
        batch_op.drop_index('message_agent_thought_app_id_idx')

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_index('message_created_by_idx')
        batch_op.drop_index('message_conversation_id_idx')
        batch_op.drop_column('image_urls')

    with op.batch_alter_table('keyword_table', schema=None) as batch_op:
        batch_op.drop_index('keyword_table_dataset_id_idx')

    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.drop_index('document_dataset_id_idx')
        batch_op.drop_index('document_batch_idx')
        batch_op.drop_index('document_account_id_idx')

    with op.batch_alter_table('dataset_query', schema=None) as batch_op:
        batch_op.drop_index('dataset_source_app_id_idx')
        batch_op.drop_index('dataset_query_dataset_id_idx')
        batch_op.drop_index('dataset_created_by_idx')

    with op.batch_alter_table('dataset', schema=None) as batch_op:
        batch_op.drop_index('dataset_account_id_name_idx')

    with op.batch_alter_table('conversation', schema=None) as batch_op:
        batch_op.drop_index('conversation_app_id_idx')
        batch_op.drop_index('conversation_app_created_by_idx')

    with op.batch_alter_table('app_dataset_join', schema=None) as batch_op:
        batch_op.drop_index('app_dataset_join_app_id_dataset_id_idx')

    with op.batch_alter_table('app', schema=None) as batch_op:
        batch_op.drop_index('app_token_idx')
        batch_op.drop_index('app_account_id_idx')
        batch_op.create_index('idx_app_account_id', ['account_id'], unique=False)
        batch_op.alter_column('account_id',
               existing_type=sa.UUID(),
               nullable=True)
        batch_op.drop_column('token')
        batch_op.drop_column('debug_conversation_id')
        batch_op.drop_column('draft_app_config_id')
        batch_op.drop_column('app_config_id')

    with op.batch_alter_table('api_tool_provider', schema=None) as batch_op:
        batch_op.drop_index('api_tool_provider_account_id_idx')
        batch_op.drop_index('api_tool_name_idx')

    with op.batch_alter_table('api_tool', schema=None) as batch_op:
        batch_op.drop_index('api_tool_provider_id_name_idx')
        batch_op.drop_index('api_tool_account_id_idx')

    with op.batch_alter_table('account_oauth', schema=None) as batch_op:
        batch_op.drop_index('account_oauth_openid_provider_idx')
        batch_op.drop_index('account_oauth_account_id_idx')

    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_index('account_email_idx')
        batch_op.drop_column('assistant_agent_conversation_id')

    with op.batch_alter_table('app_config_version', schema=None) as batch_op:
        batch_op.drop_index('app_config_version_app_id_idx')

    op.drop_table('app_config_version')
    with op.batch_alter_table('app_config', schema=None) as batch_op:
        batch_op.drop_index('app_config_app_id_idx')

    op.drop_table('app_config')
    # ### end Alembic commands ###

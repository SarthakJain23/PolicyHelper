"""add_organizations_and_llm_configs

Revision ID: a1b2c3d4e5f6
Revises: f4c8ef61433c
Create Date: 2026-09-26 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f4c8ef61433c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # 2. Create organization_llm_configs table
    op.create_table(
        'organization_llm_configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('encrypted_api_key', sa.Text(), nullable=False),
        sa.Column('key_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('default_embedding_model', sa.String(length=100), nullable=False, server_default='text-embedding-3-small'),
        sa.Column('embedding_dimensions', sa.Integer(), nullable=False, server_default='1536'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_tested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_llm_configs_organization_id'), 'organization_llm_configs', ['organization_id'], unique=False)

    # 3. Add embedding_model to document_chunks
    op.add_column('document_chunks', sa.Column('embedding_model', sa.String(length=100), nullable=True))

    # 4. Add selected_model to chat_sessions
    op.add_column('chat_sessions', sa.Column('selected_model', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_sessions', 'selected_model')
    op.drop_column('document_chunks', 'embedding_model')
    op.drop_index(op.f('ix_organization_llm_configs_organization_id'), table_name='organization_llm_configs')
    op.drop_table('organization_llm_configs')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')

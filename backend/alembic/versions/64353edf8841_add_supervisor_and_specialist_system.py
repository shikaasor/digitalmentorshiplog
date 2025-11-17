"""Add supervisor and specialist system

Revision ID: 64353edf8841
Revises: d7e753b3f250
Create Date: 2025-11-11 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '64353edf8841'
down_revision: Union[str, Sequence[str], None] = 'd7e753b3f250'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add supervisor-mentor relationship and specialist system."""

    # 1. Add supervisor_id to users table
    op.add_column('users', sa.Column('supervisor_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_users_supervisor_id', 'users', 'users', ['supervisor_id'], ['id'])
    op.create_index('ix_users_supervisor_id', 'users', ['supervisor_id'])

    # 2. Create user_specializations table
    op.create_table(
        'user_specializations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('thematic_area', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'thematic_area', name='uq_user_specialization')
    )
    op.create_index('ix_user_specializations_user_id', 'user_specializations', ['user_id'])
    op.create_index('ix_user_specializations_thematic_area', 'user_specializations', ['thematic_area'])

    # 3. Create log_comments table
    op.create_table(
        'log_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('mentorship_log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('is_specialist_comment', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['mentorship_log_id'], ['mentorship_logs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_log_comments_mentorship_log_id', 'log_comments', ['mentorship_log_id'])
    op.create_index('ix_log_comments_user_id', 'log_comments', ['user_id'])

    # 4. Create specialist_notifications table
    op.create_table(
        'specialist_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('mentorship_log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('specialist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('thematic_area', sa.String(length=100), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('notified_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['mentorship_log_id'], ['mentorship_logs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['specialist_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('mentorship_log_id', 'specialist_id', 'thematic_area', name='uq_specialist_notification')
    )
    op.create_index('ix_specialist_notifications_specialist_id', 'specialist_notifications', ['specialist_id'])
    op.create_index('ix_specialist_notifications_is_read', 'specialist_notifications', ['is_read'])


def downgrade() -> None:
    """Downgrade schema by removing supervisor and specialist system."""

    # Drop tables in reverse order
    op.drop_index('ix_specialist_notifications_is_read', table_name='specialist_notifications')
    op.drop_index('ix_specialist_notifications_specialist_id', table_name='specialist_notifications')
    op.drop_table('specialist_notifications')

    op.drop_index('ix_log_comments_user_id', table_name='log_comments')
    op.drop_index('ix_log_comments_mentorship_log_id', table_name='log_comments')
    op.drop_table('log_comments')

    op.drop_index('ix_user_specializations_thematic_area', table_name='user_specializations')
    op.drop_index('ix_user_specializations_user_id', table_name='user_specializations')
    op.drop_table('user_specializations')

    # Drop supervisor_id from users
    op.drop_index('ix_users_supervisor_id', table_name='users')
    op.drop_constraint('fk_users_supervisor_id', 'users', type_='foreignkey')
    op.drop_column('users', 'supervisor_id')

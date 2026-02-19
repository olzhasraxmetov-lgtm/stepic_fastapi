"""create UserCourseProgressORM

Revision ID: d1124bbf217f
Revises: 78dcb7a26ea2
Create Date: 2026-02-19 13:52:52.043570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1124bbf217f'
down_revision: Union[str, None] = '78dcb7a26ea2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_course_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('current_lesson_id', sa.Integer(), nullable=True),
    sa.Column('progress_percentage', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('last_accessed', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['current_lesson_id'], ['lessons.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'course_id', name='_user_course_progress_uc')
    )


def downgrade() -> None:
    op.drop_table('user_course_progress')

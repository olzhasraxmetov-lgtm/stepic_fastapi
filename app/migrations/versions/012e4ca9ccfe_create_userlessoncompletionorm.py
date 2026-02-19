"""create UserLessonCompletionORM

Revision ID: 012e4ca9ccfe
Revises: d1124bbf217f
Create Date: 2026-02-19 13:59:24.428810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '012e4ca9ccfe'
down_revision: Union[str, None] = 'd1124bbf217f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_lesson_completions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_completion_uc')
    )


def downgrade() -> None:
    op.drop_table('user_lesson_completions')

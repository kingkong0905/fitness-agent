"""create training_plans table

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "training_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("generated_plan", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_plans_user_id", "training_plans", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_training_plans_user_id", table_name="training_plans")
    op.drop_table("training_plans")

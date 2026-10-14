"""create member_profiles table

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "member_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("fitness_level", sa.String(20), nullable=False),
        sa.Column("goals", sa.Text(), nullable=False),
        sa.Column("available_days", sa.String(255), nullable=False),
        sa.Column("equipment", sa.Text(), nullable=False),
        sa.Column("health_notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_member_profiles_user_id"),
    )


def downgrade() -> None:
    op.drop_table("member_profiles")

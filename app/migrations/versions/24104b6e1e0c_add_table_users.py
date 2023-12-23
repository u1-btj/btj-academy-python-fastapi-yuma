"""add_table_users

Revision ID: 24104b6e1e0c
Revises: a8483365f505
Create Date: 2021-06-20 08:28:35.834586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "24104b6e1e0c"
down_revision = "a8483365f505"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
        sa.Column("deactivated_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_by", sa.Integer, sa.ForeignKey("users.user_id"), nullable=True
        ),
        sa.Column(
            "updated_by", sa.Integer, sa.ForeignKey("users.user_id"), nullable=True
        ),
        sa.Column(
            "deactivated_by", sa.Integer, sa.ForeignKey("users.user_id"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_table("user")

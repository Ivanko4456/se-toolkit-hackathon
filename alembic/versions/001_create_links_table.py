"""create links table

Revision ID: 001
Revises:
Create Date: 2026-04-03
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use native PostgreSQL ARRAY for tags column
    # For SQLite (tests), the model uses TypeDecorator which renders as TEXT
    op.create_table(
        "links",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("tags", sa.Text, nullable=False, server_default="'[]'"),
        sa.Column("user_id", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_links_user_id", "links", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_links_user_id", table_name="links")
    op.drop_table("links")

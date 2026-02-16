"""Add model_pricing table

Revision ID: 9a2b3c4d5e6f
Revises: b2c3d4e5f6a7
Create Date: 2026-02-16 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from open_webui.migrations.util import get_existing_tables

revision: str = "9a2b3c4d5e6f"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = set(get_existing_tables())
    if "model_pricing" in existing_tables:
        return

    op.create_table(
        "model_pricing",
        sa.Column("model_id", sa.Text(), primary_key=True),
        sa.Column("provider", sa.Text(), nullable=True),
        sa.Column("input_usd_per_million", sa.Float(), nullable=True),
        sa.Column("output_usd_per_million", sa.Float(), nullable=True),
        sa.Column("context_window", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=True),
    )

    op.create_index("idx_model_pricing_model_id", "model_pricing", ["model_id"]) 


def downgrade() -> None:
    op.drop_index("idx_model_pricing_model_id", table_name="model_pricing")
    op.drop_table("model_pricing")

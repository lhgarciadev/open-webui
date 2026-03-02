"""Add user_budget and spending_transaction tables

Revision ID: d4e5f6a7b8c9
Revises: 9a2b3c4d5e6f
Create Date: 2026-03-02 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from open_webui.migrations.util import get_existing_tables

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "9a2b3c4d5e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = set(get_existing_tables())

    if "user_budget" not in existing_tables:
        op.create_table(
            "user_budget",
            sa.Column("user_id", sa.Text(), primary_key=True),
            sa.Column("initial_budget", sa.Numeric(12, 6), nullable=False),
            sa.Column("current_balance", sa.Numeric(12, 6), nullable=False),
            sa.Column("hard_limit", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
            sa.Column("updated_at", sa.BigInteger(), nullable=False),
        )
        op.create_index("idx_user_budget_user_id", "user_budget", ["user_id"])

    if "spending_transaction" not in existing_tables:
        op.create_table(
            "spending_transaction",
            sa.Column("id", sa.Text(), primary_key=True),
            sa.Column("user_id", sa.Text(), nullable=False),
            sa.Column("chat_id", sa.Text(), nullable=False),
            sa.Column("message_id", sa.Text(), nullable=False),
            sa.Column("model_id", sa.Text(), nullable=False),
            sa.Column("input_tokens", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
            sa.Column("output_tokens", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
            sa.Column("input_cost_usd", sa.Numeric(12, 6), nullable=False, server_default=sa.text("0")),
            sa.Column("output_cost_usd", sa.Numeric(12, 6), nullable=False, server_default=sa.text("0")),
            sa.Column("total_cost_usd", sa.Numeric(12, 6), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
        )
        op.create_index("idx_spending_tx_user_id", "spending_transaction", ["user_id"])
        op.create_index("idx_spending_tx_created", "spending_transaction", ["user_id", "created_at"])
        op.create_index("idx_spending_tx_chat_id", "spending_transaction", ["chat_id"])


def downgrade() -> None:
    op.drop_index("idx_spending_tx_chat_id", table_name="spending_transaction")
    op.drop_index("idx_spending_tx_created", table_name="spending_transaction")
    op.drop_index("idx_spending_tx_user_id", table_name="spending_transaction")
    op.drop_table("spending_transaction")

    op.drop_index("idx_user_budget_user_id", table_name="user_budget")
    op.drop_table("user_budget")

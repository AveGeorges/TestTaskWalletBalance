"""create wallets and operations

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

operation_type_enum = postgresql.ENUM(
    "DEPOSIT",
    "WITHDRAW",
    name="operation_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute("CREATE TYPE operation_type AS ENUM ('DEPOSIT', 'WITHDRAW')")
    op.create_table(
        "wallets",
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_wallets_uuid"), "wallets", ["uuid"], unique=False)
    op.create_table(
        "operations",
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("operation_type", operation_type_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_operations_uuid"), "operations", ["uuid"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_operations_uuid"), table_name="operations")
    op.drop_table("operations")
    op.drop_index(op.f("ix_wallets_uuid"), table_name="wallets")
    op.drop_table("wallets")
    op.execute("DROP TYPE operation_type")

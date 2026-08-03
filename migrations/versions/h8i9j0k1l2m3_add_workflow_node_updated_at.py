"""add missing workflow_node_runs updated_at column

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-08-03 01:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # WorkflowNodeRun inherits TimestampMixin, but the original workflow-table
    # migration omitted this column. Keep a server default so upgrades with
    # existing node rows remain safe and the schema matches the ORM contract.
    op.add_column(
        "workflow_node_runs",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("workflow_node_runs", "updated_at")

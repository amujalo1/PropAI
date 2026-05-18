"""Add owner_id to properties table

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-18

Properties are now user-scoped. Each property has an owner_id FK to users.
Existing properties get owner_id = NULL (admins can still see them all).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "properties",
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_properties_owner_id", "properties")
    op.drop_column("properties", "owner_id")

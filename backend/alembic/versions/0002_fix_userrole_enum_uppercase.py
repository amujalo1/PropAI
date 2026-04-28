"""Fix userrole enum to use uppercase values

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-28

The userrole enum was created with lowercase values (admin, agent, …)
but SQLAlchemy sends the enum key name which is uppercase (ADMIN, AGENT, …).
This migration recreates the enum with uppercase values.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add a temporary text column
    op.add_column("users", sa.Column("role_tmp", sa.String(50), nullable=True))

    # 2. Copy current values uppercased into the temp column
    op.execute("""
        UPDATE users SET role_tmp = UPPER(REPLACE(role::text, ' ', '_'))
    """)

    # 3. Drop the old enum column
    op.drop_column("users", "role")

    # 4. Drop the old enum type
    op.execute("DROP TYPE IF EXISTS userrole")

    # 5. Create the new enum with uppercase values
    op.execute("""
        CREATE TYPE userrole AS ENUM ('ADMIN', 'DATA_STEWARD', 'CI_OWNER', 'AGENT')
    """)

    # 6. Add the new column using the new enum
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("ADMIN", "DATA_STEWARD", "CI_OWNER", "AGENT", name="userrole"),
            nullable=True,
        ),
    )

    # 7. Copy temp values into the new column
    op.execute("UPDATE users SET role = role_tmp::userrole")

    # 8. Set NOT NULL and drop temp column
    op.alter_column("users", "role", nullable=False)
    op.drop_column("users", "role_tmp")


def downgrade() -> None:
    op.add_column("users", sa.Column("role_tmp", sa.String(50), nullable=True))
    op.execute("UPDATE users SET role_tmp = LOWER(role::text)")
    op.drop_column("users", "role")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("""
        CREATE TYPE userrole AS ENUM ('admin', 'data_steward', 'ci_owner', 'agent')
    """)
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("admin", "data_steward", "ci_owner", "agent", name="userrole"),
            nullable=True,
        ),
    )
    op.execute("UPDATE users SET role = role_tmp::userrole")
    op.alter_column("users", "role", nullable=False)
    op.drop_column("users", "role_tmp")

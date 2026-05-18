"""Fix propertytype and propertystatus enums to uppercase

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-18

propertytype was created with lowercase values (residential, commercial, land)
but SQLAlchemy sends the enum key name which is uppercase (RESIDENTIAL, ...).
Same issue for propertystatus (DRAFT, ACTIVE, etc. — these were already
uppercase in the DB so only propertytype needs fixing).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Fix propertytype: lowercase → uppercase
    # residential → RESIDENTIAL, commercial → COMMERCIAL, land → LAND
    # ------------------------------------------------------------------

    # 1. Add temp column
    op.add_column("properties", sa.Column("type_tmp", sa.String(50), nullable=True))

    # 2. Copy uppercased values
    op.execute("UPDATE properties SET type_tmp = UPPER(type::text)")

    # 3. Drop old enum column
    op.drop_column("properties", "type")

    # 4. Drop old enum type
    op.execute("DROP TYPE IF EXISTS propertytype")

    # 5. Recreate with uppercase values
    op.execute("CREATE TYPE propertytype AS ENUM ('RESIDENTIAL', 'COMMERCIAL', 'LAND')")

    # 6. Add new column
    op.add_column(
        "properties",
        sa.Column(
            "type",
            sa.Enum("RESIDENTIAL", "COMMERCIAL", "LAND", name="propertytype"),
            nullable=True,
        ),
    )

    # 7. Copy values back
    op.execute("UPDATE properties SET type = type_tmp::propertytype")

    # 8. Set NOT NULL, drop temp
    op.alter_column("properties", "type", nullable=False)
    op.drop_column("properties", "type_tmp")


def downgrade() -> None:
    op.add_column("properties", sa.Column("type_tmp", sa.String(50), nullable=True))
    op.execute("UPDATE properties SET type_tmp = LOWER(type::text)")
    op.drop_column("properties", "type")
    op.execute("DROP TYPE IF EXISTS propertytype")
    op.execute("CREATE TYPE propertytype AS ENUM ('residential', 'commercial', 'land')")
    op.add_column(
        "properties",
        sa.Column(
            "type",
            sa.Enum("residential", "commercial", "land", name="propertytype"),
            nullable=True,
        ),
    )
    op.execute("UPDATE properties SET type = type_tmp::propertytype")
    op.alter_column("properties", "type", nullable=False)
    op.drop_column("properties", "type_tmp")

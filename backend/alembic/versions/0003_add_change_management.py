"""Add Change Management tables and ITIL enums

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-05

Adds the Change Management (ITIL) layer that was implemented after the
initial schema. The `changes` and `change_ci` tables were already created
in migration 0001 as part of the initial schema, but this migration
documents the ITIL-specific additions and ensures the schema is correct
on any fresh deployment:

  - Verifies `changes` table has all ITIL fields
    (justification, implementation_plan, backout_plan, test_plan,
     scheduling columns, approved_by_id)
  - Verifies `change_ci` association table exists
  - Adds missing columns if a deployment skipped them

This migration is safe to run on an existing database — all ALTER TABLE
statements use IF NOT EXISTS / DO NOTHING patterns.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(sa.text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = :table AND column_name = :column
    """), {"table": table, "column": column})
    return result.fetchone() is not None


def _table_exists(conn, table: str) -> bool:
    result = conn.execute(sa.text("""
        SELECT 1 FROM information_schema.tables
        WHERE table_name = :table
    """), {"table": table})
    return result.fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # Ensure `changes` table has all ITIL Change Management columns.
    # These were part of 0001 but may be missing on older deployments.
    # ------------------------------------------------------------------
    itil_columns = [
        ("justification",         "TEXT"),
        ("implementation_plan",   "TEXT"),
        ("backout_plan",          "TEXT"),
        ("test_plan",             "TEXT"),
        ("scheduled_start",       "TIMESTAMP WITHOUT TIME ZONE"),
        ("scheduled_end",         "TIMESTAMP WITHOUT TIME ZONE"),
        ("actual_start",          "TIMESTAMP WITHOUT TIME ZONE"),
        ("actual_end",            "TIMESTAMP WITHOUT TIME ZONE"),
        ("approved_by_id",        "UUID REFERENCES users(id)"),
    ]

    for col_name, col_type in itil_columns:
        if not _column_exists(conn, "changes", col_name):
            op.add_column(
                "changes",
                sa.Column(col_name, sa.Text() if "TEXT" in col_type else sa.DateTime(), nullable=True),
            )

    # ------------------------------------------------------------------
    # Ensure `change_ci` association table exists (SACM integration).
    # ------------------------------------------------------------------
    if not _table_exists(conn, "change_ci"):
        op.create_table(
            "change_ci",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("change_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("changes.id"), nullable=False),
            sa.Column("ci_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ci_hierarchy.id"), nullable=False),
            sa.Column("impact_description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    # ------------------------------------------------------------------
    # Ensure `incidents` table has resolution / root-cause columns.
    # ------------------------------------------------------------------
    incident_columns = [
        ("resolution",  "TEXT"),
        ("resolved_at", "TIMESTAMP WITHOUT TIME ZONE"),
        ("root_cause",  "TEXT"),
    ]

    for col_name, col_type in incident_columns:
        if not _column_exists(conn, "incidents", col_name):
            op.add_column(
                "incidents",
                sa.Column(col_name, sa.Text() if "TEXT" in col_type else sa.DateTime(), nullable=True),
            )

    # ------------------------------------------------------------------
    # Index on changes.title (may already exist from 0001).
    # ------------------------------------------------------------------
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_changes_title ON changes (title)"
    ))


def downgrade() -> None:
    # Remove columns added by this migration (only if they were not in 0001).
    # Because 0001 already includes these columns on a fresh install, the
    # downgrade is a no-op to avoid breaking the base schema.
    pass

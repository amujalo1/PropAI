"""Initial schema — users, properties, changes, incidents, ci_hierarchy, change_ci

Revision ID: 0001
Revises: 
Create Date: 2026-04-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "data_steward", "ci_owner", "agent", name="userrole"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "type",
            sa.Enum("residential", "commercial", "land", name="propertytype"),
            nullable=False,
        ),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT", "PENDING_REVIEW", "ACTIVE", "RESERVED",
                "SOLD", "RENTED", "SUSPENDED", "ARCHIVED",
                name="propertystatus",
            ),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(15, 2), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_properties_name", "properties", ["name"])

    # ------------------------------------------------------------------
    # changes  (parent table for Incident via joined-table inheritance)
    # ------------------------------------------------------------------
    op.create_table(
        "changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("record_type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "change_type",
            sa.Enum("STANDARD", "NORMAL", "EMERGENCY", name="changetype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT", "SUBMITTED", "APPROVED", "REJECTED",
                "IN_PROGRESS", "COMPLETED", "FAILED", "CLOSED",
                name="changestatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("P1", "P2", "P3", "P4", name="changepriority"),
            nullable=False,
        ),
        sa.Column(
            "risk",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="changerisk"),
            nullable=False,
        ),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("implementation_plan", sa.Text(), nullable=True),
        sa.Column("backout_plan", sa.Text(), nullable=True),
        sa.Column("test_plan", sa.Text(), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(), nullable=True),
        sa.Column("actual_start", sa.DateTime(), nullable=True),
        sa.Column("actual_end", sa.DateTime(), nullable=True),
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_changes_title", "changes", ["title"])

    # ------------------------------------------------------------------
    # incidents  (child table — joined-table inheritance from changes)
    # ------------------------------------------------------------------
    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), sa.ForeignKey("changes.id"), primary_key=True),
        sa.Column("incident_number", sa.String(20), nullable=True, unique=True),
        sa.Column(
            "impact",
            sa.Enum("EXTENSIVE", "SIGNIFICANT", "MODERATE", "MINOR", name="incidentimpact"),
            nullable=False,
        ),
        sa.Column(
            "urgency",
            sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="incidenturgency"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "HARDWARE", "SOFTWARE", "NETWORK", "SECURITY",
                "FACILITY", "SERVICE_REQUEST", "OTHER",
                name="incidentcategory",
            ),
            nullable=False,
        ),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
    )
    op.create_index("ix_incidents_number", "incidents", ["incident_number"])

    # ------------------------------------------------------------------
    # ci_hierarchy
    # ------------------------------------------------------------------
    op.create_table(
        "ci_hierarchy",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ci_id", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column(
            "type",
            sa.Enum("Location", "Complex", "Building", "Property", "Component", name="citype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "MAINTENANCE", "RETIRED", "PLANNED", name="cistatus"),
            nullable=False,
        ),
        sa.Column("region", sa.String(50), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("hierarchy_level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("location_detail", sa.String(255), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ci_hierarchy.id"), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ci_hierarchy_ci_id", "ci_hierarchy", ["ci_id"])

    # ------------------------------------------------------------------
    # change_ci  (SACM: which CIs are affected by a change)
    # ------------------------------------------------------------------
    op.create_table(
        "change_ci",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("change_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("changes.id"), nullable=False),
        sa.Column("ci_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ci_hierarchy.id"), nullable=False),
        sa.Column("impact_description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("change_ci")
    op.drop_index("ix_ci_hierarchy_ci_id", "ci_hierarchy")
    op.drop_table("ci_hierarchy")
    op.drop_index("ix_incidents_number", "incidents")
    op.drop_table("incidents")
    op.drop_index("ix_changes_title", "changes")
    op.drop_table("changes")
    op.drop_index("ix_properties_name", "properties")
    op.drop_table("properties")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")

    # Drop enums
    for enum_name in [
        "userrole", "propertytype", "propertystatus",
        "changetype", "changestatus", "changepriority", "changerisk",
        "incidentimpact", "incidenturgency", "incidentcategory",
        "citype", "cistatus",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

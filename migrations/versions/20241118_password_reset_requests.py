"""Create password reset requests table

Revision ID: password_reset_requests
Revises: add_active_flag
Create Date: 2025-11-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "password_reset_requests"
down_revision = "add_active_flag"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("password_reset_requests"):
        op.create_table(
            "password_reset_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("user_type", sa.String(length=20), nullable=False),
            sa.Column("email", sa.String(length=120), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("admin_note", sa.String(length=255)),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("resolved_at", sa.DateTime()),
            sa.Column("resolved_by", sa.Integer(), sa.ForeignKey("admins.id")),
        )

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("password_reset_requests")}
    if "ix_password_reset_requests_status" not in existing_indexes:
        op.create_index(
            "ix_password_reset_requests_status",
            "password_reset_requests",
            ["status"],
        )
    if "ix_password_reset_requests_created_at" not in existing_indexes:
        op.create_index(
            "ix_password_reset_requests_created_at",
            "password_reset_requests",
            ["created_at"],
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("password_reset_requests"):
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("password_reset_requests")}
        if "ix_password_reset_requests_created_at" in existing_indexes:
            op.drop_index("ix_password_reset_requests_created_at", table_name="password_reset_requests")
        if "ix_password_reset_requests_status" in existing_indexes:
            op.drop_index("ix_password_reset_requests_status", table_name="password_reset_requests")
        op.drop_table("password_reset_requests")


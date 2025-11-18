"""Add active flag to user tables

Revision ID: add_active_flag
Revises: 
Create Date: 2025-11-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_active_flag"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("customers") as batch_op:
        batch_op.add_column(
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true())
        )
    with op.batch_alter_table("staff_members") as batch_op:
        batch_op.add_column(
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true())
        )
    with op.batch_alter_table("admins") as batch_op:
        batch_op.add_column(
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true())
        )

    # drop the default so future inserts rely on SQLAlchemy default
    with op.batch_alter_table("customers") as batch_op:
        batch_op.alter_column("active", server_default=None)
    with op.batch_alter_table("staff_members") as batch_op:
        batch_op.alter_column("active", server_default=None)
    with op.batch_alter_table("admins") as batch_op:
        batch_op.alter_column("active", server_default=None)


def downgrade():
    with op.batch_alter_table("customers") as batch_op:
        batch_op.drop_column("active")
    with op.batch_alter_table("staff_members") as batch_op:
        batch_op.drop_column("active")
    with op.batch_alter_table("admins") as batch_op:
        batch_op.drop_column("active")


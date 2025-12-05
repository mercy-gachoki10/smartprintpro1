"""merge_migration_heads

Revision ID: ee07d9f4e671
Revises: 20241204_staff_to_vendor, ed4eb26dae61
Create Date: 2025-12-05 11:07:15.623992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee07d9f4e671'
down_revision = ('20241204_staff_to_vendor', 'ed4eb26dae61')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

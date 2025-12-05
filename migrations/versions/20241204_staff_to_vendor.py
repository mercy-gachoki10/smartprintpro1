"""Rename staff_members to vendors and add vendor fields

Revision ID: 20241204_staff_to_vendor
Revises: 
Create Date: 2025-12-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241204_staff_to_vendor'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Rename table from staff_members to vendors
    op.rename_table('staff_members', 'vendors')
    
    # Add vendor-specific columns
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('business_name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('business_address', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('business_type', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('services_offered', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('tax_id', sa.String(length=50), nullable=True))
    
    # Update business_name from full_name for existing vendors
    op.execute("UPDATE vendors SET business_name = full_name WHERE business_name IS NULL")
    
    # Make business_name not nullable now
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.alter_column('business_name', nullable=False)


def downgrade():
    # Remove vendor-specific columns
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.drop_column('tax_id')
        batch_op.drop_column('services_offered')
        batch_op.drop_column('business_type')
        batch_op.drop_column('business_address')
        batch_op.drop_column('business_name')
    
    # Rename table back to staff_members
    op.rename_table('vendors', 'staff_members')

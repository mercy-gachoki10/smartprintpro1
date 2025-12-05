"""Multi-vendor quotes workflow

Revision ID: 20241205_multi_vendor
Revises: 
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241205_multi_vendor'
down_revision = 'ee07d9f4e671'
branch_labels = None
depends_on = None


def upgrade():
    # Add vendor_id to quotes table
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vendor_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_quotes_vendor', 'vendors', ['vendor_id'], ['id'])
    
    # Add service_category and selected_quote_id to orders table
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_category', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('selected_quote_id', sa.Integer(), nullable=True))
    
    # Populate service_category from first order_item for existing orders
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE orders 
        SET service_category = (
            SELECT service_category 
            FROM order_items 
            WHERE order_items.order_id = orders.id 
            LIMIT 1
        )
        WHERE service_category IS NULL
    """))
    
    # Populate vendor_id in quotes from order.vendor_id for existing quotes
    conn.execute(sa.text("""
        UPDATE quotes 
        SET vendor_id = (
            SELECT vendor_id 
            FROM orders 
            WHERE orders.id = quotes.order_id
        )
        WHERE vendor_id IS NULL AND EXISTS (
            SELECT 1 FROM orders WHERE orders.id = quotes.order_id AND orders.vendor_id IS NOT NULL
        )
    """))
    
    # Make service_category NOT NULL after populating
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('service_category', nullable=False)
    
    # Make vendor_id NOT NULL in quotes after populating
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.alter_column('vendor_id', nullable=False)


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('selected_quote_id')
        batch_op.drop_column('service_category')
    
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_quotes_vendor', type_='foreignkey')
        batch_op.drop_column('vendor_id')

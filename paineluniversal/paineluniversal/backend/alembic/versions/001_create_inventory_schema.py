"""Create inventory schema and tables

Revision ID: 001_inventory
Revises: 
Create Date: 2025-08-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_inventory'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create inventory schema
    op.execute('CREATE SCHEMA IF NOT EXISTS inventory')
    
    # Create ENUM types
    op.execute("CREATE TYPE inventory.movement_type_enum AS ENUM ('IN', 'OUT', 'TRANSFER', 'ADJUSTMENT')")
    op.execute("CREATE TYPE inventory.reason_direction_enum AS ENUM ('IN', 'OUT', 'BOTH')")
    op.execute("CREATE TYPE inventory.location_type_enum AS ENUM ('principal', 'bar', 'deposito')")
    
    # Categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_categories_org_active', 'organization_id', 'is_active'),
        schema='inventory'
    )
    
    # Units table
    op.create_table(
        'units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('factor_to_base', sa.Numeric(18, 6), nullable=False, default=1.0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        schema='inventory'
    )
    
    # Products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(100), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('base_unit_id', sa.Integer(), nullable=False),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('min_stock', sa.Numeric(18, 3), nullable=False, default=0),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['inventory.categories.id']),
        sa.ForeignKeyConstraint(['base_unit_id'], ['inventory.units.id']),
        sa.Index('idx_products_org_active', 'organization_id', 'is_active'),
        sa.Index('idx_products_sku', 'sku'),
        sa.Index('idx_products_barcode', 'barcode'),
        schema='inventory'
    )
    
    # Locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', postgresql.ENUM('principal', 'bar', 'deposito', name='location_type_enum', schema='inventory'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_locations_org_active', 'organization_id', 'is_active'),
        schema='inventory'
    )
    
    # Movement reasons table
    op.create_table(
        'movement_reasons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('direction', postgresql.ENUM('IN', 'OUT', 'BOTH', name='reason_direction_enum', schema='inventory'), nullable=False),
        sa.Column('affects_cost', sa.Boolean(), nullable=False, default=True),
        sa.Column('accounting_code', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_movement_reasons_org_direction', 'organization_id', 'direction'),
        schema='inventory'
    )
    
    # Stock movements table (header)
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', postgresql.ENUM('IN', 'OUT', 'TRANSFER', 'ADJUSTMENT', name='movement_type_enum', schema='inventory'), nullable=False),
        sa.Column('reason_id', sa.Integer(), nullable=True),
        sa.Column('document_ref', sa.String(100), nullable=True),
        sa.Column('document_date', sa.Date(), nullable=False),
        sa.Column('location_from_id', sa.Integer(), nullable=True),
        sa.Column('location_to_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('status', sa.String(20), nullable=False, default='completed'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['reason_id'], ['inventory.movement_reasons.id']),
        sa.ForeignKeyConstraint(['location_from_id'], ['inventory.locations.id']),
        sa.ForeignKeyConstraint(['location_to_id'], ['inventory.locations.id']),
        sa.Index('idx_stock_movements_org_date', 'organization_id', 'document_date'),
        sa.Index('idx_stock_movements_document_ref', 'document_ref'),
        sa.Index('idx_stock_movements_type', 'movement_type'),
        schema='inventory'
    )
    
    # Stock movement lines table
    op.create_table(
        'stock_movement_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('movement_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('qty', sa.Numeric(18, 3), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 6), nullable=True),
        sa.Column('qty_base', sa.Numeric(18, 3), nullable=False),
        sa.Column('value_total', sa.Numeric(18, 6), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['movement_id'], ['inventory.stock_movements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['inventory.products.id']),
        sa.ForeignKeyConstraint(['unit_id'], ['inventory.units.id']),
        sa.Index('idx_stock_movement_lines_movement', 'movement_id'),
        sa.Index('idx_stock_movement_lines_product', 'product_id'),
        schema='inventory'
    )
    
    # Stock levels table (current position)
    op.create_table(
        'stock_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('on_hand', sa.Numeric(18, 3), nullable=False, default=0),
        sa.Column('reserved', sa.Numeric(18, 3), nullable=False, default=0),
        sa.Column('cost_avg', sa.Numeric(18, 6), nullable=False, default=0),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['inventory.products.id']),
        sa.ForeignKeyConstraint(['location_id'], ['inventory.locations.id']),
        sa.UniqueConstraint('organization_id', 'product_id', 'location_id', name='uq_stock_levels_org_product_location'),
        sa.Index('idx_stock_levels_org_location', 'organization_id', 'location_id'),
        sa.Index('idx_stock_levels_product', 'product_id'),
        schema='inventory'
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('stock_levels', schema='inventory')
    op.drop_table('stock_movement_lines', schema='inventory')
    op.drop_table('stock_movements', schema='inventory')
    op.drop_table('movement_reasons', schema='inventory')
    op.drop_table('locations', schema='inventory')
    op.drop_table('products', schema='inventory')
    op.drop_table('units', schema='inventory')
    op.drop_table('categories', schema='inventory')
    
    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS inventory.movement_type_enum")
    op.execute("DROP TYPE IF EXISTS inventory.reason_direction_enum")
    op.execute("DROP TYPE IF EXISTS inventory.location_type_enum")
    
    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS inventory CASCADE')

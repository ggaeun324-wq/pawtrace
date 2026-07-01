"""add commerce: sellers, coupons, orders, order_items + product columns

Revision ID: b7c1a2d3e4f5
Revises: c744a39763a8
Create Date: 2026-07-01 17:10:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'b7c1a2d3e4f5'
down_revision: str | None = 'c744a39763a8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 판매자(소상공인/수제작가)
    op.create_table(
        'sellers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('contact', sa.String(length=120), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 상품에 커머스 컬럼 추가(기존 행 보존을 위해 server_default 지정)
    op.add_column('products', sa.Column('seller_id', sa.Integer(), nullable=True))
    op.add_column('products', sa.Column('stock', sa.Integer(), nullable=False, server_default='0'))
    op.add_column(
        'products', sa.Column('donation_rate', sa.Integer(), nullable=False, server_default='0')
    )
    op.create_index(op.f('ix_products_seller_id'), 'products', ['seller_id'], unique=False)
    op.create_foreign_key('fk_products_seller_id', 'products', 'sellers', ['seller_id'], ['id'])

    # 쿠폰(분기 기록 보상 등)
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=40), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column(
            'status',
            sa.Enum('issued', 'used', 'expired', name='couponstatus'),
            nullable=False,
        ),
        sa.Column('source', sa.String(length=40), nullable=True),
        sa.Column('journey_entry_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['journey_entry_id'], ['journey_entries.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_coupons_user_id'), 'coupons', ['user_id'], unique=False)
    op.create_index(
        op.f('ix_coupons_journey_entry_id'), 'coupons', ['journey_entry_id'], unique=False
    )
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)

    # 주문(결제 트랜잭션)
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'status',
            sa.Enum('pending', 'paid', 'cancelled', name='orderstatus'),
            nullable=False,
        ),
        sa.Column('total_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('donation_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('coupon_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    # 주문 상세
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(
        op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_table('orders')
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
    op.drop_index(op.f('ix_coupons_code'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_journey_entry_id'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_user_id'), table_name='coupons')
    op.drop_table('coupons')
    sa.Enum(name='couponstatus').drop(op.get_bind(), checkfirst=True)
    op.drop_constraint('fk_products_seller_id', 'products', type_='foreignkey')
    op.drop_index(op.f('ix_products_seller_id'), table_name='products')
    op.drop_column('products', 'donation_rate')
    op.drop_column('products', 'stock')
    op.drop_column('products', 'seller_id')
    op.drop_table('sellers')

"""fist migration

Revision ID: 05ad019f758a
Revises: 
Create Date: 2023-12-05 14:19:17.970138

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '05ad019f758a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('productOrder',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('order_id', 'product_id')
    )
    op.create_table('userMarkets',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('market_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'market_id')
    )
    op.create_table('userOrders',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'order_id')
    )
    op.drop_table('userorders')
    op.drop_table('productorder')
    op.drop_table('usermarkets')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_ibfk_1', type_='foreignkey')
        batch_op.drop_column('role_id')
        batch_op.drop_column('about_me')
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', mysql.VARCHAR(length=64), nullable=True))
        batch_op.add_column(sa.Column('about_me', mysql.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('role_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('users_ibfk_1', 'roles', ['role_id'], ['id'])

    op.create_table('usermarkets',
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('market_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['market_id'], ['markets.id'], name='usermarkets_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='usermarkets_ibfk_2'),
    sa.PrimaryKeyConstraint('user_id', 'market_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('productorder',
    sa.Column('order_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name='productorder_ibfk_1'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='productorder_ibfk_2'),
    sa.PrimaryKeyConstraint('order_id', 'product_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('userorders',
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('order_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name='userorders_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='userorders_ibfk_2'),
    sa.PrimaryKeyConstraint('user_id', 'order_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('userOrders')
    op.drop_table('userMarkets')
    op.drop_table('productOrder')
    # ### end Alembic commands ###
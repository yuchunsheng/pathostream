"""empty message

Revision ID: 65668ba72269
Revises: dd87aeb1747e
Create Date: 2022-01-01 17:38:51.938149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65668ba72269'
down_revision = 'dd87aeb1747e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pcu_lookup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('part_type', sa.String(length=100), nullable=True),
    sa.Column('jk_type', sa.String(length=50), nullable=True),
    sa.Column('new_jk_class', sa.String(length=10), nullable=True),
    sa.Column('new_jk_pcu', sa.Float(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pcu_lookup_timestamp'), 'pcu_lookup', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pcu_lookup_timestamp'), table_name='pcu_lookup')
    op.drop_table('pcu_lookup')
    # ### end Alembic commands ###

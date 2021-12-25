"""empty message

Revision ID: 233d8ac26181
Revises: d5bf4c64299e
Create Date: 2021-12-25 16:10:20.096496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '233d8ac26181'
down_revision = 'd5bf4c64299e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cases', sa.Column('status', sa.String(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cases', 'status')
    # ### end Alembic commands ###

"""Created column for copernica id

Revision ID: 404db3c1f74
Revises: 2d257d93329
Create Date: 2016-09-10 10:16:21.981697

"""

# revision identifiers, used by Alembic.
revision = '404db3c1f74'
down_revision = '2d257d93329'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('copernica_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'copernica_id')
    ### end Alembic commands ###

"""empty message

Revision ID: 084d9ac64644
Revises: 8dbe0e7c3ca6
Create Date: 2023-08-19 22:18:31.280733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '084d9ac64644'
down_revision = '8dbe0e7c3ca6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('siprequests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=106), nullable=True))
        batch_op.add_column(sa.Column('customer_id', sa.String(length=106), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('siprequests', schema=None) as batch_op:
        batch_op.drop_column('customer_id')
        batch_op.drop_column('name')

    # ### end Alembic commands ###

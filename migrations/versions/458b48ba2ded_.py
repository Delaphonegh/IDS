"""empty message

Revision ID: 458b48ba2ded
Revises: df815aa39d63
Create Date: 2023-09-06 16:30:52.860723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '458b48ba2ded'
down_revision = 'df815aa39d63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('startblock', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('endblock', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('blocksused', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('blockid', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('company_id', sa.String(), nullable=True))
        batch_op.drop_column('biography')
        batch_op.drop_column('completed_year')
        batch_op.drop_column('index_number')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('index_number', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('completed_year', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('biography', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('company_id')
        batch_op.drop_column('blockid')
        batch_op.drop_column('blocksused')
        batch_op.drop_column('endblock')
        batch_op.drop_column('startblock')

    # ### end Alembic commands ###

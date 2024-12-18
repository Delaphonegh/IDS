"""empty message

Revision ID: 1089f9244194
Revises: ffcc38d30686
Create Date: 2024-04-27 21:30:42.844507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1089f9244194'
down_revision = 'ffcc38d30686'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('knowledgebases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('template', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('knowledgebases', schema=None) as batch_op:
        batch_op.drop_column('template')
        batch_op.drop_column('name')

    # ### end Alembic commands ###

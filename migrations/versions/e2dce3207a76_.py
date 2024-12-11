"""empty message

Revision ID: e2dce3207a76
Revises: ce7a1be1d91d
Create Date: 2023-07-06 23:58:59.109202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2dce3207a76'
down_revision = 'ce7a1be1d91d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('index_number', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_results', schema=None) as batch_op:
        batch_op.drop_column('index_number')

    # ### end Alembic commands ###

"""empty message

Revision ID: ce7a1be1d91d
Revises: 18d6a66ff2e9
Create Date: 2023-07-06 13:20:13.561810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce7a1be1d91d'
down_revision = '18d6a66ff2e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_results', schema=None) as batch_op:
        batch_op.drop_column('year')

    # ### end Alembic commands ###

"""empty message

Revision ID: e88e673e8aa7
Revises: 389579c0c9cc
Create Date: 2023-01-12 18:29:06.205171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e88e673e8aa7'
down_revision = '389579c0c9cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meeting_link', sa.String(length=250), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_column('meeting_link')

    # ### end Alembic commands ###

"""empty message

Revision ID: 97107346a654
Revises: e1bebbe823e1
Create Date: 2022-12-14 20:28:13.325349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97107346a654'
down_revision = 'e1bebbe823e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_notes', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('therapist_notes', sa.String(length=250), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_column('therapist_notes')
        batch_op.drop_column('user_notes')

    # ### end Alembic commands ###

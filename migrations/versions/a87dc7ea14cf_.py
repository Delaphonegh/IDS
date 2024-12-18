"""empty message

Revision ID: a87dc7ea14cf
Revises: 80cedae3bf6f
Create Date: 2023-05-25 14:44:40.810832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a87dc7ea14cf'
down_revision = '80cedae3bf6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ecom_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sms_attempts', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ecom_request', schema=None) as batch_op:
        batch_op.drop_column('sms_attempts')

    # ### end Alembic commands ###

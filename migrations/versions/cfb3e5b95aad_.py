"""empty message

Revision ID: cfb3e5b95aad
Revises: dbdfc866bc1f
Create Date: 2024-12-15 10:17:51.454365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfb3e5b95aad'
down_revision = 'dbdfc866bc1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('call_logs', schema=None) as batch_op:
        batch_op.drop_column('amount')

    # ### end Alembic commands ###

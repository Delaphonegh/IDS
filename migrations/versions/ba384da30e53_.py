"""empty message

Revision ID: ba384da30e53
Revises: f9eb4a35c1f1
Create Date: 2024-04-29 20:14:06.660952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba384da30e53'
down_revision = 'f9eb4a35c1f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('knowledgebases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('audio_location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('response_type', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('knowledgebases', schema=None) as batch_op:
        batch_op.drop_column('response_type')
        batch_op.drop_column('audio_location')

    # ### end Alembic commands ###

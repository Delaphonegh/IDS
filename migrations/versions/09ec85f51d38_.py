"""empty message

Revision ID: 09ec85f51d38
Revises: 59130d61238a
Create Date: 2022-06-29 22:44:36.784176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09ec85f51d38'
down_revision = '59130d61238a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('web_feature', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=40), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('web_feature', schema=None) as batch_op:
        batch_op.drop_column('email')

    # ### end Alembic commands ###

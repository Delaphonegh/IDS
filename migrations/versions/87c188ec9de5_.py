"""empty message

Revision ID: 87c188ec9de5
Revises: 281edb263104
Create Date: 2022-07-05 13:51:17.940052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87c188ec9de5'
down_revision = '281edb263104'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rookings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rookings',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_rookings')
    )
    # ### end Alembic commands ###

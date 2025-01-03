"""empty message

Revision ID: c68f50296060
Revises: 72285eee5b03
Create Date: 2022-07-03 05:56:15.475639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c68f50296060'
down_revision = '72285eee5b03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usertherapysessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('booking_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], name=op.f('fk_usertherapysessions_booking_id_bookings')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_usertherapysessions_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usertherapysessions'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usertherapysessions')
    # ### end Alembic commands ###

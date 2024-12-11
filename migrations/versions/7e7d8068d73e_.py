"""empty message

Revision ID: 7e7d8068d73e
Revises: d4422e416ce9
Create Date: 2022-07-06 00:32:06.422649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e7d8068d73e'
down_revision = 'd4422e416ce9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usertherapysessions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usertherapysessions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('booking_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], name='fk_usertherapysessions_booking_id_bookings'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_usertherapysessions_user_id_users'),
    sa.PrimaryKeyConstraint('id', name='pk_usertherapysessions')
    )
    # ### end Alembic commands ###

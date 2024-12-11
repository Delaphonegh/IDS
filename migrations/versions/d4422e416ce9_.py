"""empty message

Revision ID: d4422e416ce9
Revises: 87c188ec9de5
Create Date: 2022-07-05 13:52:33.361021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4422e416ce9'
down_revision = '87c188ec9de5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_bookings_therapist_id_users', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_bookings_user_id_users'), 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_bookings_therapist_id_webfeatures'), 'webfeatures', ['therapist_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_bookings_therapist_id_webfeatures'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_bookings_user_id_users'), type_='foreignkey')
        batch_op.create_foreign_key('fk_bookings_therapist_id_users', 'users', ['therapist_id'], ['id'])
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###

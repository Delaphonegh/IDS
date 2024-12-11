"""empty message

Revision ID: 356a24906360
Revises: d08716439f61
Create Date: 2022-07-27 00:32:37.877396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '356a24906360'
down_revision = 'd08716439f61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('therapist_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_users_therapist_id_webfeatures'), 'webfeatures', ['therapist_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_users_therapist_id_webfeatures'), type_='foreignkey')
        batch_op.drop_column('therapist_id')

    # ### end Alembic commands ###

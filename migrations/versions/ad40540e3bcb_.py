"""empty message

Revision ID: ad40540e3bcb
Revises: 9c2d984b63a5
Create Date: 2023-01-13 13:19:40.889998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad40540e3bcb'
down_revision = '9c2d984b63a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('appointment_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_notes_appointment_id_appointments'), 'appointments', ['appointment_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_notes_appointment_id_appointments'), type_='foreignkey')
        batch_op.drop_column('appointment_id')

    # ### end Alembic commands ###

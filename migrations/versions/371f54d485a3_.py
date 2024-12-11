"""empty message

Revision ID: 371f54d485a3
Revises: a42bcd910345
Create Date: 2024-04-28 19:19:13.301787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '371f54d485a3'
down_revision = 'a42bcd910345'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('price', sa.String(length=64), nullable=True),
    sa.Column('numberofchatbots', sa.String(length=64), nullable=True),
    sa.Column('requestspermonth', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plans'))
    )
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plan_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_organizations_plan_id_plans'), 'plans', ['plan_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_organizations_plan_id_plans'), type_='foreignkey')
        batch_op.drop_column('plan_id')

    op.drop_table('plans')
    # ### end Alembic commands ###

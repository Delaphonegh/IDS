"""empty message

Revision ID: ff92117feab4
Revises: bd13c853479f
Create Date: 2023-07-05 18:12:58.599087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff92117feab4'
down_revision = 'bd13c853479f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('subject', sa.String(length=128), nullable=False),
    sa.Column('result', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_student_results'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_results')
    # ### end Alembic commands ###

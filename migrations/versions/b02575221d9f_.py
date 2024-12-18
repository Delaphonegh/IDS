"""empty message

Revision ID: b02575221d9f
Revises: 23aa322ca2ac
Create Date: 2024-04-27 14:03:50.399038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b02575221d9f'
down_revision = '23aa322ca2ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_created', sa.Date(), nullable=True))

    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_created', sa.Date(), nullable=True))

    with op.batch_alter_table('conversationhistories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_created', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conversationhistories', schema=None) as batch_op:
        batch_op.drop_column('date_created')

    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.drop_column('date_created')

    with op.batch_alter_table('chatbots', schema=None) as batch_op:
        batch_op.drop_column('date_created')

    # ### end Alembic commands ###

"""empty message

Revision ID: db8b09e2a3ff
Revises: 57fc742d45dd
Create Date: 2023-11-11 13:27:06.085038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db8b09e2a3ff'
down_revision = '57fc742d45dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('issuecomments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('parent_comment_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=255), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], name=op.f('fk_issuecomments_issue_id_issues')),
    sa.ForeignKeyConstraint(['parent_comment_id'], ['issuecomments.id'], name=op.f('fk_issuecomments_parent_comment_id_issuecomments')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_issuecomments_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_issuecomments'))
    )
    op.drop_table('comments')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('issue_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('parent_comment_id', sa.INTEGER(), nullable=True),
    sa.Column('content', sa.VARCHAR(length=255), nullable=True),
    sa.Column('date', sa.DATE(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], name='fk_comments_issue_id_issues'),
    sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.id'], name='fk_comments_parent_comment_id_comments'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_comments_user_id_users'),
    sa.PrimaryKeyConstraint('id', name='pk_comments')
    )
    op.drop_table('issuecomments')
    # ### end Alembic commands ###

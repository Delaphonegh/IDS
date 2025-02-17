"""empty message

Revision ID: 16a823c9f0ab
Revises: 662fe4e42b8d
Create Date: 2023-11-12 22:18:38.430041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16a823c9f0ab'
down_revision = '662fe4e42b8d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('favorites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('likeable_id', sa.Integer(), nullable=False),
    sa.Column('likeable_type', sa.String(length=50), nullable=False),
    sa.Column('poll_id', sa.Integer(), nullable=True),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.Column('discussion_id', sa.Integer(), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id'], name=op.f('fk_favorites_discussion_id_discussions')),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], name=op.f('fk_favorites_issue_id_issues')),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_favorites_organization_id_organizations')),
    sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], name=op.f('fk_favorites_poll_id_polls')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_favorites_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_favorites'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('favorites')
    # ### end Alembic commands ###

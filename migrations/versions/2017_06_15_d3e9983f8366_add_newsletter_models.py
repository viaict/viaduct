"""Add newsletter models.

Revision ID: d3e9983f8366
Revises: 8fc09a727a5c
Create Date: 2017-06-15 22:44:02.778366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e9983f8366'
down_revision = '8fc09a727a5c'


def upgrade():
    op.create_table(
        'newsletter',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_newsletter')),
        sqlite_autoincrement=True
    )
    op.create_table(
        'newsletter_news',
        sa.Column('newsletter_id', sa.Integer(), nullable=True),
        sa.Column('news_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['news_id'], ['news.id'],
            name=op.f('fk_newsletter_news_news_id_news')),
        sa.ForeignKeyConstraint(
            ['newsletter_id'], ['newsletter.id'],
            name=op.f('fk_newsletter_news_newsletter_id_newsletter'))
    )
    op.create_table(
        'newsletter_activities',
        sa.Column('newsletter_id', sa.Integer(), nullable=True),
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['activity_id'], ['activity.id'],
            name=op.f('fk_newsletter_activities_activity_id_activity')),
        sa.ForeignKeyConstraint(
            ['newsletter_id'], ['newsletter.id'],
            name=op.f('fk_newsletter_activities_newsletter_id_newsletter'))
    )


def downgrade():
    op.drop_table('newsletter_activities')
    op.drop_table('newsletter_news')
    op.drop_table('newsletter')

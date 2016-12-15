"""add plate table

Revision ID: 88fa93c68dab
Revises: 3311cbf4b2bd
Create Date: 2016-12-05 15:08:07.137235

"""

# revision identifiers, used by Alembic.
revision = '88fa93c68dab'
down_revision = '3311cbf4b2bd'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('plate_id', sa.String(length=16), nullable=False),
    sa.Column('signed_by', sa.Integer(), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('method_document', sa.Integer(), nullable=True),
    sa.Column('method_version', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['signed_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('plate_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('plate')
    ### end Alembic commands ###

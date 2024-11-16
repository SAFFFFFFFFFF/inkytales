"""Add author_bio column to Book table

Revision ID: 276df1f1da6a
Revises: f4ec1823112f
Create Date: 2024-11-15 19:46:03.508271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '276df1f1da6a'
down_revision = 'f4ec1823112f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_bio', sa.Text(), nullable=True))
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.alter_column('image_url',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
        batch_op.alter_column('image_url',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('author_bio')

    # ### end Alembic commands ###

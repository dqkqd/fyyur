"""Initial migration.

Revision ID: baad36f8899e
Revises: 
Create Date: 2023-07-28 07:03:30.899068

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "baad36f8899e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Artist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=120), nullable=True),
        sa.Column("genres", sa.String(length=120), nullable=True),
        sa.Column("image_link", sa.String(length=500), nullable=True),
        sa.Column("facebook_link", sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Venue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("address", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=120), nullable=True),
        sa.Column("image_link", sa.String(length=500), nullable=True),
        sa.Column("facebook_link", sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("Venue")
    op.drop_table("Artist")
    # ### end Alembic commands ###

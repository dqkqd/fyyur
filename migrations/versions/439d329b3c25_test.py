"""Remove nullable=False

Revision ID: 439d329b3c25
Revises: f6023a252aeb
Create Date: 2023-07-30 21:41:51.759168

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "439d329b3c25"
down_revision = "f6023a252aeb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column("seeking_venue", existing_type=sa.BOOLEAN(), nullable=False)

    with op.batch_alter_table("Genre", schema=None) as batch_op:
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=False)

    with op.batch_alter_table("Show", schema=None) as batch_op:
        batch_op.alter_column("artist_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("venue_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column(
            "start_time", existing_type=postgresql.TIMESTAMP(), nullable=False
        )

    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column(
            "seeking_talent", existing_type=sa.BOOLEAN(), nullable=False
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.alter_column("seeking_talent", existing_type=sa.BOOLEAN(), nullable=True)
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=True)

    with op.batch_alter_table("Show", schema=None) as batch_op:
        batch_op.alter_column(
            "start_time", existing_type=postgresql.TIMESTAMP(), nullable=True
        )
        batch_op.alter_column("venue_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("artist_id", existing_type=sa.INTEGER(), nullable=True)

    with op.batch_alter_table("Genre", schema=None) as batch_op:
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=True)

    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.alter_column("seeking_venue", existing_type=sa.BOOLEAN(), nullable=True)
        batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=True)

    # ### end Alembic commands ###

"""Change website to website_link

Revision ID: f6023a252aeb
Revises: 28d4390250b8
Create Date: 2023-07-30 14:17:33.043095

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6023a252aeb"
down_revision = "28d4390250b8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.alter_column("website", new_column_name="website_link")

    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.alter_column("website", new_column_name="website_link")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.alter_column("website_link", new_column_name="website")

    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.alter_column("website_link", new_column_name="website")

    # ### end Alembic commands ###

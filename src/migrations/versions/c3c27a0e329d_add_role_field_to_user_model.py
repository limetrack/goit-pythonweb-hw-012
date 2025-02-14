"""Add role field to User model

Revision ID: c3c27a0e329d
Revises: 68c3e4abc947
Create Date: 2025-02-02 17:11:00.004447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3c27a0e329d"
down_revision: Union[str, None] = "68c3e4abc947"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role_enum = sa.Enum("USER", "ADMIN", name="userrole")


def upgrade() -> None:
    user_role_enum.create(op.get_bind())

    op.add_column(
        "users",
        sa.Column("role", user_role_enum, nullable=False, server_default="USER"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")

    user_role_enum.drop(op.get_bind())

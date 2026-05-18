"""files path to uri

Revision ID: 511daa971226
Revises: 6418b97bd0fc
Create Date: 2026-05-17 17:06:22.486188

"""

from collections.abc import Sequence

from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "511daa971226"
down_revision: str | Sequence[str] | None = "6418b97bd0fc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "file", "asset_path", nullable=False, new_column_name="uri", existing_type=mysql.VARCHAR(length=255)
    )
    op.create_unique_constraint(None, "file", ["uri"])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "file", type_="unique")
    op.alter_column("file", "uri", nullable=True, new_column_name="asset_path", existing_type=mysql.VARCHAR(length=255))
    # ### end Alembic commands ###

"""migrate_note_category_to_relation

Revision ID: 274c9b7dd915
Revises: 0613c410fe2b
Create Date: 2026-05-17 20:28:53.050594

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "274c9b7dd915"
down_revision: Union[str, Sequence[str], None] = "0613c410fe2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CATEGORY_NAMES = ("work", "personal", "finance", "learning", "other")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_categories_id"), "categories", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_categories_name"), "categories", ["name"], unique=True
    )
    category_table = sa.table(
        "categories",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
    )
    op.bulk_insert(
        category_table,
        [{"name": name} for name in CATEGORY_NAMES],
    )

    op.add_column(
        "notes", sa.Column("category_id", sa.Integer(), nullable=True)
    )
    op.execute(
        """
        UPDATE notes
        SET category_id = categories.id
        FROM categories
        WHERE notes.category = categories.name
        """
    )
    op.alter_column("notes", "category_id", nullable=False)
    op.create_foreign_key(
        "fk_notes_category_id_categories",
        "notes",
        "categories",
        ["category_id"],
        ["id"],
    )
    op.drop_column("notes", "category")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "notes",
        sa.Column(
            "category", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.execute(
        """
        UPDATE notes
        SET category = categories.name
        FROM categories
        WHERE notes.category_id = categories.id
        """
    )
    op.alter_column("notes", "category", nullable=False)
    op.drop_constraint(
        "fk_notes_category_id_categories", "notes", type_="foreignkey"
    )
    op.drop_column("notes", "category_id")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")

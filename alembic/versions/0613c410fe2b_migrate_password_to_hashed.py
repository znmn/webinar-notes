"""Migrate password to hashed

Revision ID: 0613c410fe2b
Revises: 6150ec2519df
Create Date: 2026-05-17 19:21:54.716800

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = "0613c410fe2b"
down_revision: Union[str, Sequence[str], None] = "6150ec2519df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_hashed_password(password: str) -> bool:
    return password.startswith(
        ("$2a$", "$2b$", "$2y$", "$bcrypt-sha256$", "pbkdf2_sha256$")
    )


def upgrade() -> None:
    """Migrate existing plain passwords to secure hashes."""
    bind = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("password", sa.String()),
    )

    rows = bind.execute(sa.select(users.c.id, users.c.password)).all()
    for user_id, password in rows:
        if not password:
            continue
        if _is_hashed_password(password):
            continue
        bind.execute(
            users.update()
            .where(users.c.id == user_id)
            .values(password=get_password_hash(password))
        )


def downgrade() -> None:
    """Irreversible data migration.

    Password hashes are one-way, so the original plain passwords cannot be
    reconstructed safely.
    """
    # No-op by design. Downgrade keeps hashed values in `users.password`.

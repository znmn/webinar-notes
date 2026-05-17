from collections.abc import Iterable

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.category import DEFAULT_CATEGORY_NAMES, Category


def seed_categories(
    db: Session, category_names: Iterable[str] = DEFAULT_CATEGORY_NAMES
) -> int:
    """Upsert category rows and return number of newly inserted records."""
    names = tuple(dict.fromkeys(category_names))
    if not names:
        return 0

    dialect = db.bind.dialect.name if db.bind is not None else ""

    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = pg_insert(Category).values([{"name": name} for name in names])
        stmt = stmt.on_conflict_do_nothing(index_elements=[Category.name])
        result = db.execute(stmt)
        return result.rowcount or 0

    if dialect == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        stmt = sqlite_insert(Category).values(
            [{"name": name} for name in names]
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=[Category.name])
        result = db.execute(stmt)
        return result.rowcount or 0

    existing = {
        row[0]
        for row in db.execute(
            sa.select(Category.name).where(Category.name.in_(names))
        ).all()
    }
    missing = [Category(name=name) for name in names if name not in existing]
    if missing:
        db.add_all(missing)
    return len(missing)

from app.db.seeds.categories import seed_categories
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        inserted_count = seed_categories(db)
        db.commit()
    finally:
        db.close()

    print(f"Category seeding complete. Inserted: {inserted_count}")


if __name__ == "__main__":
    main()

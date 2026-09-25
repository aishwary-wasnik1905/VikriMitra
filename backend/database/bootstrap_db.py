from pathlib import Path

from sqlalchemy import text

from backend.app.database import engine
from backend.database.load_data import load_all_data


BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_FILE = BASE_DIR / "backend" / "database" / "schema.sql"


def initialize_schema():
    print("Initializing VikriMitra database schema...")

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.execute(text(schema_sql))

    print("Database schema initialized successfully.")


def database_already_loaded() -> bool:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM orders")
        )
        order_count = result.scalar_one()

    return order_count > 0


def bootstrap_database():
    initialize_schema()

    if database_already_loaded():
        print("Database already contains Olist data. Skipping CSV reload.")
        return

    print("Database is empty. Loading Olist datasets...")
    load_all_data()
    print("Database bootstrap completed successfully.")


if __name__ == "__main__":
    bootstrap_database()
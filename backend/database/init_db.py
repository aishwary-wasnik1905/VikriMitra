from pathlib import Path

from sqlalchemy import text

from backend.app.database import engine


BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_FILE = BASE_DIR / "backend" / "database" / "schema.sql"


def initialize_database():
    print("Initializing VikriMitra database...")

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.execute(text(schema_sql))

    print("Database schema initialized successfully.")


if __name__ == "__main__":
    initialize_database()

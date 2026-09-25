from sqlalchemy import text

from backend.app.database import engine


TABLES = [
    "customers",
    "sellers",
    "products",
    "category_translation",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "geolocation",
]


def verify_data():
    with engine.connect() as connection:
        for table in TABLES:
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )
            count = result.scalar()

            print(f"{table:25} {count:>10,}")


if __name__ == "__main__":
    print("VikriMitra database verification")
    print("-" * 40)

    verify_data()
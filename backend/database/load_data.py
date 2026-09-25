import csv
from pathlib import Path

from sqlalchemy import text

from backend.app.database import engine


# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# CSV directory
DATA_DIR = BASE_DIR / "data"


def read_csv(filename):
    """Read a CSV file and return rows as dictionaries."""
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def clean(value):
    """Convert empty CSV values to None."""
    if value == "":
        return None
    return value


def load_customers(connection):
    rows = read_csv("olist_customers_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO customers (
                    customer_id,
                    customer_unique_id,
                    customer_zip_code_prefix,
                    customer_city,
                    customer_state
                )
                VALUES (
                    :customer_id,
                    :customer_unique_id,
                    :customer_zip_code_prefix,
                    :customer_city,
                    :customer_state
                )
                ON CONFLICT (customer_id) DO NOTHING
            """),
            {
                "customer_id": row["customer_id"],
                "customer_unique_id": row["customer_unique_id"],
                "customer_zip_code_prefix": int(row["customer_zip_code_prefix"]),
                "customer_city": row["customer_city"],
                "customer_state": row["customer_state"],
            },
        )

    print(f"Customers loaded: {len(rows):,}")


def load_sellers(connection):
    rows = read_csv("olist_sellers_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO sellers (
                    seller_id,
                    seller_zip_code_prefix,
                    seller_city,
                    seller_state
                )
                VALUES (
                    :seller_id,
                    :seller_zip_code_prefix,
                    :seller_city,
                    :seller_state
                )
                ON CONFLICT (seller_id) DO NOTHING
            """),
            {
                "seller_id": row["seller_id"],
                "seller_zip_code_prefix": int(row["seller_zip_code_prefix"]),
                "seller_city": row["seller_city"],
                "seller_state": row["seller_state"],
            },
        )

    print(f"Sellers loaded: {len(rows):,}")


def load_products(connection):
    rows = read_csv("olist_products_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO products (
                    product_id,
                    product_category_name,
                    product_name_length,
                    product_description_length,
                    product_photos_qty,
                    product_weight_g,
                    product_length_cm,
                    product_height_cm,
                    product_width_cm
                )
                VALUES (
                    :product_id,
                    :product_category_name,
                    :product_name_length,
                    :product_description_length,
                    :product_photos_qty,
                    :product_weight_g,
                    :product_length_cm,
                    :product_height_cm,
                    :product_width_cm
                )
                ON CONFLICT (product_id) DO NOTHING
            """),
            {
                "product_id": row["product_id"],
                "product_category_name": clean(row["product_category_name"]),
                "product_name_length": (
                    int(row["product_name_lenght"])
                    if row["product_name_lenght"]
                    else None
                ),
                "product_description_length": (
                    int(row["product_description_lenght"])
                    if row["product_description_lenght"]
                    else None
                ),
                "product_photos_qty": (
                    int(row["product_photos_qty"])
                    if row["product_photos_qty"]
                    else None
                ),
                "product_weight_g": (
                    float(row["product_weight_g"])
                    if row["product_weight_g"]
                    else None
                ),
                "product_length_cm": (
                    float(row["product_length_cm"])
                    if row["product_length_cm"]
                    else None
                ),
                "product_height_cm": (
                    float(row["product_height_cm"])
                    if row["product_height_cm"]
                    else None
                ),
                "product_width_cm": (
                    float(row["product_width_cm"])
                    if row["product_width_cm"]
                    else None
                ),
            },
        )

    print(f"Products loaded: {len(rows):,}")


def load_category_translation(connection):
    rows = read_csv("product_category_name_translation.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO category_translation (
                    product_category_name,
                    product_category_name_english
                )
                VALUES (
                    :product_category_name,
                    :product_category_name_english
                )
                ON CONFLICT (product_category_name) DO NOTHING
            """),
            {
                "product_category_name": row["product_category_name"],
                "product_category_name_english": row[
                    "product_category_name_english"
                ],
            },
        )

    print(f"Category translations loaded: {len(rows):,}")


def load_orders(connection):
    rows = read_csv("olist_orders_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    order_status,
                    order_purchase_timestamp,
                    order_approved_at,
                    order_delivered_carrier_date,
                    order_delivered_customer_date,
                    order_estimated_delivery_date
                )
                VALUES (
                    :order_id,
                    :customer_id,
                    :order_status,
                    :order_purchase_timestamp,
                    :order_approved_at,
                    :order_delivered_carrier_date,
                    :order_delivered_customer_date,
                    :order_estimated_delivery_date
                )
                ON CONFLICT (order_id) DO NOTHING
            """),
            {
                "order_id": row["order_id"],
                "customer_id": row["customer_id"],
                "order_status": row["order_status"],
                "order_purchase_timestamp": clean(
                    row["order_purchase_timestamp"]
                ),
                "order_approved_at": clean(row["order_approved_at"]),
                "order_delivered_carrier_date": clean(
                    row["order_delivered_carrier_date"]
                ),
                "order_delivered_customer_date": clean(
                    row["order_delivered_customer_date"]
                ),
                "order_estimated_delivery_date": clean(
                    row["order_estimated_delivery_date"]
                ),
            },
        )

    print(f"Orders loaded: {len(rows):,}")


def load_order_items(connection):
    rows = read_csv("olist_order_items_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO order_items (
                    order_id,
                    order_item_id,
                    product_id,
                    seller_id,
                    shipping_limit_date,
                    price,
                    freight_value
                )
                VALUES (
                    :order_id,
                    :order_item_id,
                    :product_id,
                    :seller_id,
                    :shipping_limit_date,
                    :price,
                    :freight_value
                )
                ON CONFLICT (order_id, order_item_id) DO NOTHING
            """),
            {
                "order_id": row["order_id"],
                "order_item_id": int(row["order_item_id"]),
                "product_id": clean(row["product_id"]),
                "seller_id": clean(row["seller_id"]),
                "shipping_limit_date": clean(row["shipping_limit_date"]),
                "price": float(row["price"]),
                "freight_value": float(row["freight_value"]),
            },
        )

    print(f"Order items loaded: {len(rows):,}")


def load_order_payments(connection):
    rows = read_csv("olist_order_payments_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO order_payments (
                    order_id,
                    payment_sequential,
                    payment_type,
                    payment_installments,
                    payment_value
                )
                VALUES (
                    :order_id,
                    :payment_sequential,
                    :payment_type,
                    :payment_installments,
                    :payment_value
                )
                ON CONFLICT (order_id, payment_sequential) DO NOTHING
            """),
            {
                "order_id": row["order_id"],
                "payment_sequential": int(row["payment_sequential"]),
                "payment_type": row["payment_type"],
                "payment_installments": int(row["payment_installments"]),
                "payment_value": float(row["payment_value"]),
            },
        )

    print(f"Order payments loaded: {len(rows):,}")


def load_order_reviews(connection):
    rows = read_csv("olist_order_reviews_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO order_reviews (
                    review_id,
                    order_id,
                    review_score,
                    review_comment_title,
                    review_comment_message,
                    review_creation_date,
                    review_answer_timestamp
                )
                VALUES (
                    :review_id,
                    :order_id,
                    :review_score,
                    :review_comment_title,
                    :review_comment_message,
                    :review_creation_date,
                    :review_answer_timestamp
                )
            """),
            {
                "review_id": row["review_id"],
                "order_id": row["order_id"],
                "review_score": int(row["review_score"]),
                "review_comment_title": clean(row["review_comment_title"]),
                "review_comment_message": clean(
                    row["review_comment_message"]
                ),
                "review_creation_date": clean(row["review_creation_date"]),
                "review_answer_timestamp": clean(
                    row["review_answer_timestamp"]
                ),
            },
        )

    print(f"Order reviews loaded: {len(rows):,}")


def load_geolocation(connection):
    rows = read_csv("olist_geolocation_dataset.csv")

    for row in rows:
        connection.execute(
            text("""
                INSERT INTO geolocation (
                    geolocation_zip_code_prefix,
                    geolocation_lat,
                    geolocation_lng,
                    geolocation_city,
                    geolocation_state
                )
                VALUES (
                    :geolocation_zip_code_prefix,
                    :geolocation_lat,
                    :geolocation_lng,
                    :geolocation_city,
                    :geolocation_state
                )
            """),
            {
                "geolocation_zip_code_prefix": int(
                    row["geolocation_zip_code_prefix"]
                ),
                "geolocation_lat": (
                    float(row["geolocation_lat"])
                    if row["geolocation_lat"]
                    else None
                ),
                "geolocation_lng": (
                    float(row["geolocation_lng"])
                    if row["geolocation_lng"]
                    else None
                ),
                "geolocation_city": clean(row["geolocation_city"]),
                "geolocation_state": clean(row["geolocation_state"]),
            },
        )

    print(f"Geolocation rows loaded: {len(rows):,}")


def load_all_data():
    print("Starting VikriMitra data loading...")
    print(f"Data directory: {DATA_DIR}")
    print()

    with engine.begin() as connection:
        # Parent tables first
        load_customers(connection)
        load_sellers(connection)
        load_products(connection)
        load_category_translation(connection)

        # Orders before dependent tables
        load_orders(connection)

        # Dependent tables
        load_order_items(connection)
        load_order_payments(connection)
        load_order_reviews(connection)
        load_geolocation(connection)

    print()
    print("All CSV data loaded successfully.")


if __name__ == "__main__":
    load_all_data()
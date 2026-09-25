from pathlib import Path
import csv


# Project root:
# E-Commerce Sales Analytics Chatbot/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"


DATASETS = {
    "customers": {
        "file": "olist_customers_dataset.csv",
        "key": "customer_id",
    },
    "geolocation": {
        "file": "olist_geolocation_dataset.csv",
        "key": None,
    },
    "order_items": {
        "file": "olist_order_items_dataset.csv",
        "key": None,
    },
    "order_payments": {
        "file": "olist_order_payments_dataset.csv",
        "key": None,
    },
    "order_reviews": {
        "file": "olist_order_reviews_dataset.csv",
        "key": "review_id",
    },
    "orders": {
        "file": "olist_orders_dataset.csv",
        "key": "order_id",
    },
    "products": {
        "file": "olist_products_dataset.csv",
        "key": "product_id",
    },
    "sellers": {
        "file": "olist_sellers_dataset.csv",
        "key": "seller_id",
    },
    "category_translation": {
        "file": "product_category_name_translation.csv",
        "key": "product_category_name",
    },
}


def inspect_csv(name: str, config: dict):
    file_path = DATA_DIR / config["file"]

    print("\n" + "=" * 70)
    print(f"DATASET: {name}")
    print(f"FILE:    {config['file']}")
    print("=" * 70)

    if not file_path.exists():
        print("❌ FILE NOT FOUND")
        return

    row_count = 0
    empty_values = {}
    duplicate_keys = set()
    seen_keys = set()

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        columns = reader.fieldnames

        if not columns:
            print("❌ No columns detected")
            return

        print("\nColumns:")
        for column in columns:
            print(f"  - {column}")

        for row in reader:
            row_count += 1

            # Count empty values
            for column in columns:
                value = row.get(column)

                if value is None or value.strip() == "":
                    empty_values[column] = empty_values.get(column, 0) + 1

            # Check duplicate primary-key candidate
            key = config.get("key")

            if key:
                value = row.get(key)

                if value:
                    if value in seen_keys:
                        duplicate_keys.add(value)
                    else:
                        seen_keys.add(value)

    print(f"\nRows: {row_count:,}")

    print("\nEmpty values:")

    if empty_values:
        for column, count in sorted(
            empty_values.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            percentage = (count / row_count) * 100

            print(
                f"  {column}: "
                f"{count:,} ({percentage:.2f}%)"
            )
    else:
        print("  None")

    if config.get("key"):
        print(f"\nDuplicate '{config['key']}' values:")

        if duplicate_keys:
            print(f"  ⚠️ {len(duplicate_keys):,} duplicates found")
        else:
            print("  ✅ None")

    print()


def main():
    print("=" * 70)
    print("VIKRIMITRA — OLIST DATASET INSPECTION")
    print("=" * 70)

    print(f"\nProject root: {PROJECT_ROOT}")
    print(f"Data folder:  {DATA_DIR}")

    if not DATA_DIR.exists():
        print("\n❌ Data folder does not exist!")
        return

    for name, config in DATASETS.items():
        inspect_csv(name, config)

    print("=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
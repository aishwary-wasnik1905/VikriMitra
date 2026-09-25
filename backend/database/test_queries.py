from sqlalchemy import text

from backend.app.database import engine


def run_tests():
    with engine.connect() as connection:

        # 1. Orders -> Customers
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM orders o
                JOIN customers c
                    ON o.customer_id = c.customer_id
            """)
        )
        print("Orders -> Customers:", result.scalar())

        # 2. Order Items -> Products
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM order_items oi
                JOIN products p
                    ON oi.product_id = p.product_id
            """)
        )
        print("Order Items -> Products:", result.scalar())

        # 3. Order Items -> Sellers
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM order_items oi
                JOIN sellers s
                    ON oi.seller_id = s.seller_id
            """)
        )
        print("Order Items -> Sellers:", result.scalar())

        # 4. Orders -> Payments
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM orders o
                JOIN order_payments op
                    ON o.order_id = op.order_id
            """)
        )
        print("Orders -> Payments:", result.scalar())

        # 5. Orders -> Reviews
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM orders o
                JOIN order_reviews r
                    ON o.order_id = r.order_id
            """)
        )
        print("Orders -> Reviews:", result.scalar())

        # 6. Products -> English Category
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM products p
                JOIN category_translation ct
                    ON p.product_category_name =
                       ct.product_category_name
            """)
        )
        print("Products -> Category Translation:", result.scalar())


if __name__ == "__main__":
    run_tests()
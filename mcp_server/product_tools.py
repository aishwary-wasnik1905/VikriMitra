from sqlalchemy import text

from backend.app.database import engine


def get_product_performance(
    start_date=None,
    end_date=None,
    limit: int = 10,
    category: str | None = None,
    sort_by: str = "revenue",
):
    """
    Return product/category sales performance.

    sort_by:
        - "revenue"    -> highest revenue first
        - "order_count" -> highest order volume first
    """

    if limit < 1 or limit > 100:
        return {
            "error": {
                "code": "INVALID_LIMIT",
                "message": "limit must be between 1 and 100.",
            }
        }

    if sort_by not in {
        "revenue",
        "order_count",
    }:
        return {
            "error": {
                "code": "INVALID_SORT_BY",
                "message": (
                    "sort_by must be either "
                    "'revenue' or 'order_count'."
                ),
            }
        }

    if start_date and end_date and start_date > end_date:
        return {
            "error": {
                "code": "INVALID_DATE_RANGE",
                "message": (
                    "start_date must be before or equal to end_date."
                ),
            }
        }

    conditions = []
    params = {
        "limit": limit,
    }

    if start_date:
        conditions.append(
            "o.order_purchase_timestamp >= :start_date"
        )
        params["start_date"] = start_date

    if end_date:
        conditions.append(
            "o.order_purchase_timestamp < "
            ":end_date + INTERVAL '1 day'"
        )
        params["end_date"] = end_date

    if category:
        conditions.append(
            """
            LOWER(
                COALESCE(
                    ct.product_category_name_english,
                    p.product_category_name
                )
            ) = LOWER(:category)
            """
        )
        params["category"] = category

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    order_clause = (
        "order_count DESC"
        if sort_by == "order_count"
        else "revenue DESC"
    )

    query = text(
        f"""
        SELECT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category,

            COUNT(DISTINCT o.order_id) AS order_count,

            COUNT(*) AS items_sold,

            COALESCE(
                SUM(oi.price),
                0
            ) AS revenue

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        JOIN products p
            ON oi.product_id = p.product_id

        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name

        {where_clause}

        GROUP BY category

        ORDER BY {order_clause}

        LIMIT :limit
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            params,
        ).mappings().all()

    return {
        "tool": "get_product_performance",
        "limit": limit,
        "category_filter": category,
        "sort_by": sort_by,
        "data": [
            {
                "category": row["category"],
                "order_count": int(
                    row["order_count"]
                ),
                "items_sold": int(
                    row["items_sold"]
                ),
                "revenue": float(
                    row["revenue"]
                ),
            }
            for row in rows
        ],
    }
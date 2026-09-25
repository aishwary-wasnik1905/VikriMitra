from sqlalchemy import text

from backend.app.database import engine


def get_review_analysis(
    start_date=None,
    end_date=None,
    category: str | None = None,
    group_by: str = "score",
):
    """
    Analyze customer reviews.

    group_by:
        - "score"    -> review score distribution
        - "category" -> average review score by category
        - "state"    -> average review score by customer state
    """

    allowed_groupings = {
        "score",
        "category",
        "state",
    }

    if group_by not in allowed_groupings:
        return {
            "error": {
                "code": "INVALID_GROUP_BY",
                "message": (
                    "group_by must be one of: "
                    "score, category, state."
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
    params = {}

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
        where_clause = "WHERE " + " AND ".join(conditions)

    # ---------------------------------------------------------
    # Review score distribution
    # ---------------------------------------------------------

    if group_by == "score":
        query = text(
            f"""
            SELECT
                r.review_score,
                COUNT(*) AS review_count,
                ROUND(
                    COUNT(*) * 100.0 /
                    SUM(COUNT(*)) OVER (),
                    2
                ) AS percentage
            FROM order_reviews r
            JOIN orders o
                ON r.order_id = o.order_id

            LEFT JOIN order_items oi
                ON o.order_id = oi.order_id

            LEFT JOIN products p
                ON oi.product_id = p.product_id

            LEFT JOIN category_translation ct
                ON p.product_category_name =
                   ct.product_category_name

            {where_clause}

            GROUP BY r.review_score
            ORDER BY r.review_score
            """
        )

        with engine.connect() as connection:
            rows = connection.execute(
                query,
                params,
            ).mappings().all()

        return {
            "tool": "get_review_analysis",
            "group_by": "score",
            "category_filter": category,
            "data": [
                {
                    "review_score": int(row["review_score"]),
                    "review_count": int(row["review_count"]),
                    "percentage": float(row["percentage"]),
                }
                for row in rows
            ],
        }

    # ---------------------------------------------------------
    # Average review score by category
    # ---------------------------------------------------------

    if group_by == "category":
        query = text(
            f"""
            WITH review_categories AS (
                SELECT DISTINCT
                    r.review_pk,
                    r.order_id,
                    r.review_score,
                    ct.product_category_name_english
                        AS category
                FROM order_reviews r

                JOIN orders o
                    ON r.order_id = o.order_id

                JOIN order_items oi
                    ON o.order_id = oi.order_id

                JOIN products p
                    ON oi.product_id = p.product_id

                LEFT JOIN category_translation ct
                    ON p.product_category_name =
                       ct.product_category_name

                {where_clause}
            )

            SELECT
                category,
                ROUND(
                    AVG(review_score)::numeric,
                    2
                ) AS avg_review_score,
                COUNT(*) AS review_count
            FROM review_categories
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY avg_review_score DESC, review_count DESC
            """
        )

        with engine.connect() as connection:
            rows = connection.execute(
                query,
                params,
            ).mappings().all()

        return {
            "tool": "get_review_analysis",
            "group_by": "category",
            "category_filter": category,
            "data": [
                {
                    "category": row["category"],
                    "avg_review_score": float(
                        row["avg_review_score"]
                    ),
                    "review_count": int(
                        row["review_count"]
                    ),
                }
                for row in rows
            ],
        }

    # ---------------------------------------------------------
    # Average review score by customer state
    # ---------------------------------------------------------

    if group_by == "state":
        query = text(
            f"""
            SELECT
                c.customer_state AS state,
                ROUND(
                    AVG(r.review_score)::numeric,
                    2
                ) AS avg_review_score,
                COUNT(*) AS review_count
            FROM order_reviews r

            JOIN orders o
                ON r.order_id = o.order_id

            JOIN customers c
                ON o.customer_id = c.customer_id

            {where_clause}

            GROUP BY c.customer_state
            ORDER BY avg_review_score DESC, review_count DESC
            """
        )

        with engine.connect() as connection:
            rows = connection.execute(
                query,
                params,
            ).mappings().all()

        return {
            "tool": "get_review_analysis",
            "group_by": "state",
            "category_filter": category,
            "data": [
                {
                    "state": row["state"],
                    "avg_review_score": float(
                        row["avg_review_score"]
                    ),
                    "review_count": int(
                        row["review_count"]
                    ),
                }
                for row in rows
            ],
        }

    return {
        "error": {
            "code": "UNEXPECTED_GROUP_BY",
            "message": "Unsupported review grouping.",
        }
    }
from datetime import date

from sqlalchemy import text

from backend.app.database import engine


def get_order_trends(
    start_date: date | None = None,
    end_date: date | None = None,
    granularity: str = "month",
):
    """
    Return order count and revenue trends over time.

    Revenue is calculated from order_items.price.

    Parameters:
        start_date: Optional start date.
        end_date: Optional end date.
        granularity: "day", "week", or "month".
    """

    allowed_granularities = {"day", "week", "month"}

    if granularity not in allowed_granularities:
        return {
            "error": {
                "code": "INVALID_GRANULARITY",
                "message": (
                    f"Unsupported granularity '{granularity}'. "
                    f"Use one of: {sorted(allowed_granularities)}."
                ),
            }
        }

    if start_date and end_date and start_date > end_date:
        return {
            "error": {
                "code": "INVALID_DATE_RANGE",
                "message": "start_date must be before or equal to end_date.",
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
            "o.order_purchase_timestamp < :end_date + INTERVAL '1 day'"
        )
        params["end_date"] = end_date

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = text(
        f"""
        SELECT
            DATE_TRUNC(
                '{granularity}',
                o.order_purchase_timestamp
            ) AS period,
            COUNT(DISTINCT o.order_id) AS order_count,
            COALESCE(SUM(oi.price), 0) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        {where_clause}
        GROUP BY period
        ORDER BY period
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(query, params).mappings().all()

    return {
        "tool": "get_order_trends",
        "granularity": granularity,
        "data": [
            {
                "period": row["period"].isoformat(),
                "order_count": int(row["order_count"]),
                "revenue": float(row["revenue"]),
            }
            for row in rows
        ],
    }
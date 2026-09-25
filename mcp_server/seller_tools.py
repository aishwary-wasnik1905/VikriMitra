from sqlalchemy import text

from backend.app.database import engine


def get_seller_performance(
    start_date=None,
    end_date=None,
    limit: int = 10,
    state: str | None = None,
):
    """
    Return seller performance ranked by revenue.
    """

    if limit < 1 or limit > 100:
        return {
            "error": {
                "code": "INVALID_LIMIT",
                "message": "limit must be between 1 and 100.",
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
    params = {"limit": limit}

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

    if state:
        conditions.append(
            "UPPER(s.seller_state) = UPPER(:state)"
        )
        params["state"] = state

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = text(
        f"""
        SELECT
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT o.order_id) AS order_count,
            COUNT(*) AS items_sold,
            COALESCE(SUM(oi.price), 0) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN sellers s
            ON oi.seller_id = s.seller_id
        {where_clause}
        GROUP BY
            s.seller_id,
            s.seller_city,
            s.seller_state
        ORDER BY revenue DESC
        LIMIT :limit
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(query, params).mappings().all()

    return {
        "tool": "get_seller_performance",
        "limit": limit,
        "state_filter": state,
        "data": [
            {
                "seller_id": row["seller_id"],
                "seller_city": row["seller_city"],
                "seller_state": row["seller_state"],
                "order_count": int(row["order_count"]),
                "items_sold": int(row["items_sold"]),
                "revenue": float(row["revenue"]),
            }
            for row in rows
        ],
    }
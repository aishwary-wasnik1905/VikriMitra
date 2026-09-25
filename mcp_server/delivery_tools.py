from sqlalchemy import text

from backend.app.database import engine


def get_delivery_performance(
    start_date=None,
    end_date=None,
    state: str | None = None,
):
    """
    Analyze delivery performance by customer state.

    delay_days:
        Actual delivery date - estimated delivery date.

    Positive delay_days = delivered late.
    Negative delay_days = delivered early.
    """

    if start_date and end_date and start_date > end_date:
        return {
            "error": {
                "code": "INVALID_DATE_RANGE",
                "message": "start_date must be before or equal to end_date.",
            }
        }

    conditions = [
        "o.order_delivered_customer_date IS NOT NULL",
        "o.order_estimated_delivery_date IS NOT NULL",
    ]

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

    if state:
        conditions.append(
            "UPPER(c.customer_state) = UPPER(:state)"
        )
        params["state"] = state

    where_clause = " AND ".join(conditions)

    query = text(
        f"""
        SELECT
            c.customer_state AS state,

            COUNT(DISTINCT o.order_id) AS delivered_orders,

            ROUND(
                AVG(
                    EXTRACT(
                        EPOCH FROM (
                            o.order_delivered_customer_date
                            - o.order_estimated_delivery_date
                        )
                    ) / 86400.0
                ),
                2
            ) AS avg_delay_days,

            COUNT(*) FILTER (
                WHERE o.order_delivered_customer_date
                    > o.order_estimated_delivery_date
            ) AS late_orders,

            ROUND(
                COUNT(*) FILTER (
                    WHERE o.order_delivered_customer_date
                        > o.order_estimated_delivery_date
                ) * 100.0 /
                NULLIF(COUNT(*), 0),
                2
            ) AS late_percentage

        FROM orders o

        JOIN customers c
            ON o.customer_id = c.customer_id

        WHERE {where_clause}

        GROUP BY c.customer_state

        ORDER BY avg_delay_days DESC
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(query, params).mappings().all()

    return {
        "tool": "get_delivery_performance",
        "state_filter": state,
        "data": [
            {
                "state": row["state"],
                "delivered_orders": int(row["delivered_orders"]),
                "avg_delay_days": float(row["avg_delay_days"]),
                "late_orders": int(row["late_orders"]),
                "late_percentage": float(row["late_percentage"]),
            }
            for row in rows
        ],
    }
from sqlalchemy import text

from backend.app.database import engine


def get_payment_breakdown(
    start_date=None,
    end_date=None,
):
    """
    Return payment method distribution by payment value.
    """

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
            op.payment_type,
            COUNT(DISTINCT op.order_id) AS order_count,
            COALESCE(SUM(op.payment_value), 0) AS payment_value,
            ROUND(
                COALESCE(SUM(op.payment_value), 0) * 100.0 /
                SUM(SUM(op.payment_value)) OVER (),
                2
            ) AS percentage
        FROM order_payments op
        JOIN orders o
            ON op.order_id = o.order_id
        {where_clause}
        GROUP BY op.payment_type
        ORDER BY payment_value DESC
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(query, params).mappings().all()

    return {
        "tool": "get_payment_breakdown",
        "data": [
            {
                "payment_type": row["payment_type"],
                "order_count": int(row["order_count"]),
                "payment_value": float(row["payment_value"]),
                "percentage": float(row["percentage"]),
            }
            for row in rows
        ],
    }
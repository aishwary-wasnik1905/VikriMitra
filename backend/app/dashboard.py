from typing import Any
import json

from sqlalchemy import text

from backend.app.database import engine


def pin_chart(
    query: str,
    chart_type: str,
    chart_config: dict[str, Any],
    insight: str | None = None,
    data_snapshot: dict[str, Any] | None = None,
):
    sql = text(
        """
        INSERT INTO dashboard_charts
        (
            query,
            chart_type,
            chart_config,
            insight,
            data_snapshot
        )
        VALUES
        (
            :query,
            :chart_type,
            CAST(:chart_config AS JSONB),
            :insight,
            CAST(:data_snapshot AS JSONB)
        )
        RETURNING
            id,
            created_at,
            updated_at
        """
    )

    with engine.begin() as conn:
        row = conn.execute(
            sql,
            {
                "query": query,
                "chart_type": chart_type,
                "chart_config": json.dumps(chart_config),
                "insight": insight,
                "data_snapshot": (
                    json.dumps(data_snapshot)
                    if data_snapshot is not None
                    else None
                ),
            },
        ).mappings().first()

    return {
        "success": True,
        "id": row["id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "message": "Chart pinned to dashboard successfully.",
    }


def get_dashboard_charts():
    sql = text(
        """
        SELECT
            id,
            query,
            chart_type,
            chart_config,
            insight,
            data_snapshot,
            created_at,
            updated_at
        FROM dashboard_charts
        ORDER BY created_at DESC
        """
    )

    with engine.begin() as conn:
        rows = conn.execute(sql).mappings().all()

    return {
        "charts": [dict(row) for row in rows]
    }


def refresh_chart(chart_id: int):
    from backend.agent.groq_agent import GroqAgent
    from backend.app.analytics_pipeline import build_response

    select_sql = text(
        """
        SELECT
            id,
            query,
            chart_type,
            chart_config,
            insight,
            data_snapshot
        FROM dashboard_charts
        WHERE id = :chart_id
        """
    )

    with engine.begin() as conn:
        row = conn.execute(
            select_sql,
            {"chart_id": chart_id},
        ).mappings().first()

    if row is None:
        return {
            "error": {
                "code": "CHART_NOT_FOUND",
                "message": "Dashboard chart not found.",
            }
        }

    try:
        agent = GroqAgent()

        agent_result = agent.process_query(
            row["query"]
        )

        refreshed = build_response(
            agent_result
        )

        if "error" in refreshed:
            return refreshed

        old_snapshot = row["data_snapshot"] or {}
        new_snapshot = refreshed.get("result") or {}

        old_data = old_snapshot.get("data", [])
        new_data = new_snapshot.get("data", [])

        significant_change = (
            len(old_data) != len(new_data)
            or old_data != new_data
        )

        update_sql = text(
            """
            UPDATE dashboard_charts
            SET
                chart_config = CAST(:chart_config AS JSONB),
                insight = :insight,
                data_snapshot = CAST(:data_snapshot AS JSONB),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :chart_id
            """
        )

        with engine.begin() as conn:
            conn.execute(
                update_sql,
                {
                    "chart_config": json.dumps(
                        refreshed["chart"]
                    ),
                    "insight": refreshed.get(
                        "insight"
                    ),
                    "data_snapshot": json.dumps(
                        refreshed.get("result")
                    ),
                    "chart_id": chart_id,
                },
            )

        return {
            "id": chart_id,
            "query": row["query"],
            "refreshed": True,
            "significant_change": significant_change,
            "previous_row_count": len(old_data),
            "new_row_count": len(new_data),
            "chart": refreshed["chart"],
            "insight": refreshed["insight"],
            "result": refreshed["result"],
        }

    except Exception as exc:
        return {
            "error": {
                "code": "REFRESH_ERROR",
                "message": str(exc),
            }
        }
from datetime import date
from typing import Any

from mcp.server import MCPServer

from backend.mcp_server.order_tools import get_order_trends
from backend.mcp_server.product_tools import get_product_performance
from backend.mcp_server.seller_tools import get_seller_performance
from backend.mcp_server.review_tools import get_review_analysis
from backend.mcp_server.payment_tools import get_payment_breakdown
from backend.mcp_server.delivery_tools import get_delivery_performance


mcp = MCPServer("VikriMitra Analytics MCP Server")


def safe_call(function, **kwargs) -> dict[str, Any]:
    """Convert unexpected tool failures into structured errors."""
    try:
        result = function(**kwargs)

        if isinstance(result, dict):
            return result

        return {
            "error": {
                "code": "INVALID_TOOL_RESPONSE",
                "message": "Analytics tool returned an invalid response.",
            }
        }

    except Exception as exc:
        return {
            "error": {
                "code": "TOOL_EXECUTION_ERROR",
                "message": str(exc),
            }
        }


@mcp.tool()
def order_trends(
    start_date: date | None = None,
    end_date: date | None = None,
    granularity: str = "month",
) -> dict[str, Any]:
    """Get order count and revenue trends over time."""
    return safe_call(
        get_order_trends,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
    )


@mcp.tool()
def product_performance(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 10,
    category: str | None = None,
    sort_by: str = "revenue",
) -> dict[str, Any]:
    """Get category performance ranked by revenue or order count."""
    return safe_call(
        get_product_performance,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        category=category,
        sort_by=sort_by,
    )


@mcp.tool()
def seller_performance(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 10,
    state: str | None = None,
) -> dict[str, Any]:
    """Get seller performance ranked by revenue."""
    return safe_call(
        get_seller_performance,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        state=state,
    )


@mcp.tool()
def review_analysis(
    start_date: date | None = None,
    end_date: date | None = None,
    category: str | None = None,
    group_by: str = "score",
) -> dict[str, Any]:
    """
    Analyze customer reviews.

    group_by:
    - score: review score distribution
    - category: average review score by category
    - state: average review score by customer state
    """
    return safe_call(
        get_review_analysis,
        start_date=start_date,
        end_date=end_date,
        category=category,
        group_by=group_by,
    )


@mcp.tool()
def payment_breakdown(
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict[str, Any]:
    """Get payment method distribution by payment value."""
    return safe_call(
        get_payment_breakdown,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
def delivery_performance(
    start_date: date | None = None,
    end_date: date | None = None,
    state: str | None = None,
) -> dict[str, Any]:
    """Get delivery performance by customer state."""
    return safe_call(
        get_delivery_performance,
        start_date=start_date,
        end_date=end_date,
        state=state,
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8001,
    )
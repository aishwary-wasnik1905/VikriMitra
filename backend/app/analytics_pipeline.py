from typing import Any

from backend.app.chart_builder import build_chart
from backend.app.response_builder import build_insight


SUPPORTED_TOOLS = {
    "order_trends",
    "product_performance",
    "seller_performance",
    "review_analysis",
    "payment_breakdown",
    "delivery_performance",
    "multi_tool",
}


def _out_of_domain_error() -> dict[str, Any]:
    return {
        "error": {
            "code": "OUT_OF_DOMAIN",
            "message": (
                "I can only answer questions about the "
                "e-commerce sales data. Try asking about "
                "sales, products, sellers, reviews, "
                "payments, or delivery performance."
            ),
        }
    }


def build_response(
    agent_result: Any,
) -> dict[str, Any]:
    """
    Convert an agent result into the final API response.
    """

    if not isinstance(agent_result, dict):
        return {
            "error": {
                "code": "INVALID_AGENT_RESPONSE",
                "message": "The analytics agent returned an invalid response.",
            }
        }

    # Preserve structured agent errors.
    if "error" in agent_result:
        return agent_result

    tool_name = agent_result.get("tool")
    arguments = agent_result.get("arguments", {})
    result = agent_result.get("result")
    chart_type = agent_result.get("chart_type")

    # Allow only known analytics tools.
    if tool_name not in SUPPORTED_TOOLS:
        return _out_of_domain_error()

    if not isinstance(arguments, dict):
        return {
            "error": {
                "code": "INVALID_AGENT_RESPONSE",
                "message": "The analytics arguments are invalid.",
            }
        }

    if not isinstance(result, dict):
        return {
            "error": {
                "code": "INVALID_AGENT_RESPONSE",
                "message": "The analytics result is invalid.",
            }
        }

    # Preserve MCP tool errors.
    if "error" in result:
        return {
            "error": result["error"]
        }

    if not chart_type or not isinstance(chart_type, str):
        return {
            "error": {
                "code": "INVALID_CHART_TYPE",
                "message": "The analytics agent did not provide a chart type.",
            }
        }

    data = result.get("data")

    if data is None:
        return {
            "error": {
                "code": "NO_DATA",
                "message": "No analytics data was returned.",
            }
        }

    if not isinstance(data, list):
        return {
            "error": {
                "code": "INVALID_RESULT_DATA",
                "message": "The analytics result data is invalid.",
            }
        }

    if len(data) == 0:
        return {
            "error": {
                "code": "NO_DATA",
                "message": "No data was found for this query.",
            }
        }

    # Build chart.
    try:
        chart = build_chart(
            tool_name,
            result,
            chart_type,
        )
    except Exception:
        return {
            "error": {
                "code": "CHART_BUILD_ERROR",
                "message": "The analytics chart could not be generated.",
            }
        }

    # Build one-line insight.
    try:
        insight = build_insight(
            tool_name,
            result,
        )
    except Exception:
        return {
            "error": {
                "code": "INSIGHT_BUILD_ERROR",
                "message": "The analytics insight could not be generated.",
            }
        }

    return {
        "agent": agent_result.get("agent"),
        "tool": tool_name,
        "arguments": arguments,
        "chart": chart,
        "insight": insight,
        "result": result,
    }
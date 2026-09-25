from typing import Any

from backend.agent.interface import ILLMAgent
from backend.mcp_server.order_tools import get_order_trends
from backend.mcp_server.product_tools import get_product_performance
from backend.mcp_server.seller_tools import get_seller_performance
from backend.mcp_server.review_tools import get_review_analysis
from backend.mcp_server.payment_tools import get_payment_breakdown
from backend.mcp_server.delivery_tools import get_delivery_performance


class FallbackAgent(ILLMAgent):
    """
    Rule-based fallback agent.

    Uses keyword matching to select an analytics tool.
    The fallback always returns a bar chart.
    """

    def process_query(self, query: str) -> dict[str, Any]:
        query_lower = query.lower().strip()

        # Payment-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "payment",
                "payments",
                "credit card",
                "boleto",
                "voucher",
                "debit card",
            ]
        ):
            result = get_payment_breakdown()

            return {
                "agent": "fallback",
                "tool": "payment_breakdown",
                "chart_type": "bar",
                "result": result,
            }

        # Review/rating-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "review",
                "reviews",
                "rating",
                "ratings",
                "rated",
                "score",
            ]
        ):
            result = get_review_analysis()

            return {
                "agent": "fallback",
                "tool": "review_analysis",
                "chart_type": "bar",
                "result": result,
            }

        # Delivery-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "delivery",
                "deliveries",
                "delay",
                "delayed",
                "late",
                "shipping",
            ]
        ):
            result = get_delivery_performance()

            return {
                "agent": "fallback",
                "tool": "delivery_performance",
                "chart_type": "bar",
                "result": result,
            }

        # Seller-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "seller",
                "sellers",
                "vendor",
                "vendors",
            ]
        ):
            result = get_seller_performance(limit=10)

            return {
                "agent": "fallback",
                "tool": "seller_performance",
                "chart_type": "bar",
                "result": result,
            }

        # Product/category-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "product",
                "products",
                "category",
                "categories",
            ]
        ):
            result = get_product_performance(limit=10)

            return {
                "agent": "fallback",
                "tool": "product_performance",
                "chart_type": "bar",
                "result": result,
            }

        # Default: order trends
        result = get_order_trends()

        return {
            "agent": "fallback",
            "tool": "order_trends",
            "chart_type": "bar",
            "result": result,
        }
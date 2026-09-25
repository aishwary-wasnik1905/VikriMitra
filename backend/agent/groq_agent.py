import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from backend.agent.interface import ILLMAgent


load_dotenv()


class GroqAgent(ILLMAgent):
    """
    Groq-backed analytics agent.

    Groq selects the appropriate analytics tool.
    The selected MCP tool is executed through the
    VikriMitra Streamable HTTP MCP server.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        )

        self.timeout_seconds = int(
            os.getenv(
                "LLM_TIMEOUT_SECONDS",
                "15",
            )
        )

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=self.api_key
        )

        self.mcp_url = os.getenv(
            "MCP_URL",
            "http://127.0.0.1:8001/mcp",
        )

    # ---------------------------------------------------------
    # MCP
    # ---------------------------------------------------------

    async def _run_mcp_query(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute an MCP tool through Streamable HTTP.
        """

        async with streamable_http_client(
            self.mcp_url
        ) as (
            read_stream,
            write_stream,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                return result.structured_content

    # ---------------------------------------------------------
    # Query detectors
    # ---------------------------------------------------------

    def _is_scatter_query(
        self,
        query: str,
    ) -> bool:
        """
        Detect scatter-plot requests.

        Supported example:
        "Show the relationship between items sold
         and revenue across the top 10 product categories."
        """

        q = query.lower()

        return (
            "scatter" in q
            or (
                "relationship" in q
                and "items sold" in q
                and "revenue" in q
            )
        )

    def _is_category_review_query(
        self,
        query: str,
    ) -> bool:
        q = query.lower()

        return (
            "review score" in q
            and "top 5" in q
            and "category" in q
            and (
                "order volume" in q
                or "order count" in q
                or "number of orders" in q
            )
        )

    def _is_state_delivery_review_query(
        self,
        query: str,
    ) -> bool:
        q = query.lower()

        return (
            "delivery" in q
            and "review score" in q
            and "state" in q
            and (
                "side by side" in q
                or "compare" in q
                or "together" in q
            )
        )

    # ---------------------------------------------------------
    # Tool definitions for Groq
    # ---------------------------------------------------------

    def _get_tool_definitions(self):

        nullable_string = {
            "type": [
                "string",
                "null",
            ]
        }

        return [

            # -------------------------------------------------
            # Order trends
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "order_trends",
                    "description": (
                        "Get order count and revenue "
                        "trends over time."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                                "description": (
                                    "Optional start date "
                                    "in YYYY-MM-DD format."
                                ),
                            },
                            "end_date": {
                                **nullable_string,
                                "description": (
                                    "Optional end date "
                                    "in YYYY-MM-DD format."
                                ),
                            },
                            "granularity": {
                                "type": "string",
                                "enum": [
                                    "day",
                                    "week",
                                    "month",
                                ],
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },

            # -------------------------------------------------
            # Product performance
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "product_performance",
                    "description": (
                        "Get product category performance "
                        "ranked by revenue or order count."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                            },
                            "end_date": {
                                **nullable_string,
                            },
                            "limit": {
                                "type": [
                                    "integer",
                                    "null",
                                ],
                                "minimum": 1,
                                "maximum": 100,
                                "description": (
                                    "Number of categories "
                                    "to return."
                                ),
                            },
                            "category": {
                                **nullable_string,
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": [
                                    "revenue",
                                    "order_count",
                                ],
                                "description": (
                                    "Sort by total revenue "
                                    "or total order count."
                                ),
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },

            # -------------------------------------------------
            # Seller performance
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "seller_performance",
                    "description": (
                        "Get seller performance "
                        "ranked by revenue."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                            },
                            "end_date": {
                                **nullable_string,
                            },
                            "limit": {
                                "type": [
                                    "integer",
                                    "null",
                                ],
                                "minimum": 1,
                                "maximum": 100,
                            },
                            "state": {
                                **nullable_string,
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },

            # -------------------------------------------------
            # Review analysis
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "review_analysis",
                    "description": (
                        "Analyze customer reviews. "
                        "Can return score distribution, "
                        "average review score by category, "
                        "or average review score by state."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                            },
                            "end_date": {
                                **nullable_string,
                            },
                            "category": {
                                **nullable_string,
                            },
                            "group_by": {
                                "type": "string",
                                "enum": [
                                    "score",
                                    "category",
                                    "state",
                                ],
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },

            # -------------------------------------------------
            # Payment breakdown
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "payment_breakdown",
                    "description": (
                        "Get payment method distribution "
                        "by payment value."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                            },
                            "end_date": {
                                **nullable_string,
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },

            # -------------------------------------------------
            # Delivery performance
            # -------------------------------------------------

            {
                "type": "function",
                "function": {
                    "name": "delivery_performance",
                    "description": (
                        "Get delivery performance "
                        "by customer state."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                **nullable_string,
                            },
                            "end_date": {
                                **nullable_string,
                            },
                            "state": {
                                **nullable_string,
                            },
                        },
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    # ---------------------------------------------------------
    # Main async query processor
    # ---------------------------------------------------------

    async def _process_query_async(
        self,
        query: str,
    ) -> dict[str, Any]:

        # =====================================================
        # Multi-tool query:
        # Top 5 categories by order volume + review scores
        # =====================================================

        if self._is_category_review_query(query):

            product_arguments = {
                "limit": 5,
                "sort_by": "order_count",
            }

            review_arguments = {
                "group_by": "category",
            }

            product_result = await self._run_mcp_query(
                "product_performance",
                product_arguments,
            )

            review_result = await self._run_mcp_query(
                "review_analysis",
                review_arguments,
            )

            product_data = product_result.get(
                "data",
                [],
            )

            review_data = review_result.get(
                "data",
                [],
            )

            review_lookup = {}

            for row in review_data:
                category = str(
                    row.get("category", "")
                ).strip().lower()

                review_lookup[category] = row

            merged_data = []

            for row in product_data:

                category = str(
                    row.get("category", "")
                ).strip().lower()

                review_row = review_lookup.get(
                    category
                )

                if review_row:
                    merged_data.append(
                        {
                            "category": category,
                            "order_count": row.get(
                                "order_count",
                                0,
                            ),
                            "avg_review_score": review_row.get(
                                "avg_review_score",
                                0,
                            ),
                            "review_count": review_row.get(
                                "review_count",
                                0,
                            ),
                        }
                    )

            return {
                "agent": "llm",
                "tool": "multi_tool",
                "tools": [
                    "product_performance",
                    "review_analysis",
                ],
                "arguments": {
                    "product_performance":
                        product_arguments,
                    "review_analysis":
                        review_arguments,
                },
                "chart_type": "horizontal_bar",
                "result": {
                    "tool":
                        "category_review_comparison",
                    "data": merged_data,
                },
            }

        # =====================================================
        # Multi-tool query:
        # Delivery delay + review score by state
        # =====================================================

        if self._is_state_delivery_review_query(query):

            delivery_arguments = {}

            review_arguments = {
                "group_by": "state",
            }

            delivery_result = await self._run_mcp_query(
                "delivery_performance",
                delivery_arguments,
            )

            review_result = await self._run_mcp_query(
                "review_analysis",
                review_arguments,
            )

            delivery_data = delivery_result.get(
                "data",
                [],
            )

            review_data = review_result.get(
                "data",
                [],
            )

            review_lookup = {}

            for row in review_data:

                state = str(
                    row.get("state", "")
                ).strip().upper()

                review_lookup[state] = row

            merged_data = []

            for row in delivery_data:

                state = str(
                    row.get("state", "")
                ).strip().upper()

                review_row = review_lookup.get(
                    state
                )

                if review_row:
                    merged_data.append(
                        {
                            "state": state,
                            "avg_delay_days": row.get(
                                "avg_delay_days",
                                0,
                            ),
                            "late_percentage": row.get(
                                "late_percentage",
                                0,
                            ),
                            "avg_review_score": review_row.get(
                                "avg_review_score",
                                0,
                            ),
                            "review_count": review_row.get(
                                "review_count",
                                0,
                            ),
                        }
                    )

            return {
                "agent": "llm",
                "tool": "multi_tool",
                "tools": [
                    "delivery_performance",
                    "review_analysis",
                ],
                "arguments": {
                    "delivery_performance":
                        delivery_arguments,
                    "review_analysis":
                        review_arguments,
                },
                "chart_type": "horizontal_bar",
                "result": {
                    "tool":
                        "state_delivery_review_comparison",
                    "data": merged_data,
                },
            }

        # =====================================================
        # Scatter plot query
        # =====================================================

        if self._is_scatter_query(query):

            arguments = {
                "limit": 10,
                "sort_by": "revenue",
            }

            tool_result = await self._run_mcp_query(
                "product_performance",
                arguments,
            )

            return {
                "agent": "llm",
                "tool": "product_performance",
                "arguments": arguments,
                "chart_type": "scatter",
                "result": tool_result,
            }

        # =====================================================
        # Normal Groq flow
        # =====================================================

        tools = self._get_tool_definitions()

        system_message = """
You are VikriMitra, an e-commerce sales analytics assistant.

Your job is to understand a user's analytics question
and select the appropriate analytics tool.

Rules:
- Use an analytics tool for data questions.
- Never invent numerical results.
- Dates must use YYYY-MM-DD.
- "top N" means limit N.
- "top by revenue" means sort_by=revenue.
- "top by order volume" means sort_by=order_count.
- "São Paulo" as a state filter means SP.
- If no date range is specified, use the full dataset.
- Optional arguments may be omitted or set to null.
- Do not invent filters the user did not request.

Review rules:
- score -> review score distribution
- category -> average review score by category
- state -> average review score by state

Payment questions:
- Use payment_breakdown.

Delivery questions:
- Use delivery_performance.

Product/category questions:
- Use product_performance.

Seller questions:
- Use seller_performance.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0,
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return {
                "agent": "llm",
                "tool": None,
                "chart_type": "bar",
                "answer": message.content or "",
                "result": None,
            }

        tool_call = message.tool_calls[0]

        tool_name = tool_call.function.name

        try:

            arguments = json.loads(
                tool_call.function.arguments
                or "{}"
            )

        except json.JSONDecodeError:

            return {
                "agent": "llm",
                "error": {
                    "code": "INVALID_TOOL_ARGUMENTS",
                    "message": (
                        "Groq returned invalid JSON "
                        "for tool arguments."
                    ),
                },
            }

        # Remove optional null values.
        arguments = {
            key: value
            for key, value in arguments.items()
            if value is not None
        }

        tool_result = await self._run_mcp_query(
            tool_name,
            arguments,
        )

        return {
            "agent": "llm",
            "tool": tool_name,
            "arguments": arguments,
            "chart_type": self._choose_chart_type(
                tool_name
            ),
            "result": tool_result,
        }

    # ---------------------------------------------------------
    # Default chart selection
    # ---------------------------------------------------------

    def _choose_chart_type(
        self,
        tool_name: str,
    ) -> str:

        if tool_name == "order_trends":
            return "line"

        if tool_name == "payment_breakdown":
            return "donut"

        if tool_name == "review_analysis":
            return "stacked_horizontal_bar"

        if tool_name == "delivery_performance":
            return "horizontal_bar"

        if tool_name in {
            "product_performance",
            "seller_performance",
        }:
            return "horizontal_bar"

        return "bar"

    # ---------------------------------------------------------
    # Public interface
    # ---------------------------------------------------------

    def process_query(
        self,
        query: str,
    ) -> dict[str, Any]:

        try:

            return asyncio.run(
                asyncio.wait_for(
                    self._process_query_async(
                        query
                    ),
                    timeout=self.timeout_seconds,
                )
            )

        except asyncio.TimeoutError:

            return {
                "agent": "llm",
                "error": {
                    "code": "LLM_TIMEOUT",
                    "message": (
                        "The LLM request exceeded "
                        "the configured timeout."
                    ),
                },
            }

        except Exception as exc:

            return {
                "agent": "llm",
                "error": {
                    "code": "LLM_AGENT_ERROR",
                    "message": str(exc),
                },
            }
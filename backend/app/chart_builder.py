from typing import Any


def build_chart(
    tool_name: str,
    result: dict[str, Any],
    chart_type: str,
) -> dict[str, Any]:

    data = result.get("data", [])

    if not data:
        return {
            "chart_type": chart_type,
            "title": "No data available",
            "labels": [],
            "datasets": [],
        }

    # ==========================================================
    # Scatter chart
    # ==========================================================

    if chart_type == "scatter":
        points = []

        for row in data:
            items_sold = row.get("items_sold")
            revenue = row.get("revenue")
            category = row.get("category")

            if items_sold is None or revenue is None:
                continue

            points.append(
                {
                    "x": float(items_sold),
                    "y": float(revenue),
                    "category": category,
                }
            )

        return {
            "chart_type": "scatter",
            "title": "Items Sold vs Revenue by Category",
            "x_axis_label": "Items Sold",
            "y_axis_label": "Revenue",
            "datasets": [
                {
                    "label": "Product Categories",
                    "data": points,
                }
            ],
        }

    # ==========================================================
    # Order trends
    # ==========================================================

    if tool_name == "order_trends":

        labels = [
            str(row.get("period", ""))[:7]
            for row in data
        ]

        return {
            "chart_type": "line",
            "title": "Orders and Revenue Over Time",
            "labels": labels,
            "datasets": [
                {
                    "label": "Orders",
                    "data": [
                        row.get("order_count", 0)
                        for row in data
                    ],
                },
                {
                    "label": "Revenue",
                    "data": [
                        row.get("revenue", 0)
                        for row in data
                    ],
                },
            ],
        }

    # ==========================================================
    # Product performance
    # ==========================================================

    if tool_name == "product_performance":

        sort_by = result.get(
            "sort_by",
            "revenue",
        )

        labels = [
            row.get("category", "")
            for row in data
        ]

        if sort_by == "order_count":
            return {
                "chart_type": chart_type,
                "title": (
                    "Top Product Categories "
                    "by Order Volume"
                ),
                "labels": labels,
                "datasets": [
                    {
                        "label": "Order Count",
                        "data": [
                            row.get(
                                "order_count",
                                0,
                            )
                            for row in data
                        ],
                    }
                ],
            }

        return {
            "chart_type": chart_type,
            "title": (
                "Top Product Categories "
                "by Revenue"
            ),
            "labels": labels,
            "datasets": [
                {
                    "label": "Revenue",
                    "data": [
                        row.get(
                            "revenue",
                            0,
                        )
                        for row in data
                    ],
                }
            ],
        }

    # ==========================================================
    # Seller performance
    # ==========================================================

    if tool_name == "seller_performance":

        return {
            "chart_type": "horizontal_bar",
            "title": "Top Sellers by Revenue",
            "labels": [
                row.get("seller_id", "")
                for row in data
            ],
            "datasets": [
                {
                    "label": "Revenue",
                    "data": [
                        row.get("revenue", 0)
                        for row in data
                    ],
                }
            ],
        }

    # ==========================================================
    # Review analysis
    # ==========================================================

    if tool_name == "review_analysis":

        group_by = result.get(
            "group_by",
            "score",
        )

        if group_by == "category":
            return {
                "chart_type": chart_type,
                "title": (
                    "Average Review Score "
                    "by Category"
                ),
                "labels": [
                    row.get("category", "")
                    for row in data
                ],
                "datasets": [
                    {
                        "label": (
                            "Average Review Score"
                        ),
                        "data": [
                            row.get(
                                "avg_review_score",
                                0,
                            )
                            for row in data
                        ],
                    }
                ],
            }

        if group_by == "state":
            return {
                "chart_type": chart_type,
                "title": (
                    "Average Review Score "
                    "by State"
                ),
                "labels": [
                    row.get("state", "")
                    for row in data
                ],
                "datasets": [
                    {
                        "label": (
                            "Average Review Score"
                        ),
                        "data": [
                            row.get(
                                "avg_review_score",
                                0,
                            )
                            for row in data
                        ],
                    }
                ],
            }

        return {
            "chart_type": chart_type,
            "title": "Review Score Distribution",
            "labels": [
                str(row.get("review_score", ""))
                for row in data
            ],
            "datasets": [
                {
                    "label": "Review Count",
                    "data": [
                        row.get(
                            "review_count",
                            0,
                        )
                        for row in data
                    ],
                }
            ],
        }

    # ==========================================================
    # Payment breakdown
    # ==========================================================

    if tool_name == "payment_breakdown":

        return {
            "chart_type": "donut",
            "title": "Payment Method Breakdown",
            "labels": [
                row.get("payment_type", "")
                for row in data
            ],
            "datasets": [
                {
                    "label": "Payment Value",
                    "data": [
                        row.get(
                            "payment_value",
                            0,
                        )
                        for row in data
                    ],
                }
            ],
        }

    # ==========================================================
    # Delivery performance
    # ==========================================================

    if tool_name == "delivery_performance":

        return {
            "chart_type": "horizontal_bar",
            "title": "Late Delivery Rate by State",
            "labels": [
                row.get("state", "")
                for row in data
            ],
            "datasets": [
                {
                    "label": "Late Delivery %",
                    "data": [
                        row.get(
                            "late_percentage",
                            0,
                        )
                        for row in data
                    ],
                }
            ],
        }

    # ==========================================================
    # Multi-tool: category review comparison
    # ==========================================================

    if tool_name == "multi_tool":

        inner_tool = result.get("tool")

        if inner_tool == "category_review_comparison":
            return {
                "chart_type": chart_type,
                "title": (
                    "Average Review Score of "
                    "Top Categories by Order Volume"
                ),
                "labels": [
                    row.get("category", "")
                    for row in data
                ],
                "datasets": [
                    {
                        "label": (
                            "Average Review Score"
                        ),
                        "data": [
                            row.get(
                                "avg_review_score",
                                0,
                            )
                            for row in data
                        ],
                    }
                ],
            }

        if inner_tool == "state_delivery_review_comparison":
            return {
                "chart_type": chart_type,
                "title": (
                    "Delivery Delay and "
                    "Review Score by State"
                ),
                "labels": [
                    row.get("state", "")
                    for row in data
                ],
                "datasets": [
                    {
                        "label": "Average Delay (Days)",
                        "data": [
                            row.get(
                                "avg_delay_days",
                                0,
                            )
                            for row in data
                        ],
                    },
                    {
                        "label": "Average Review Score",
                        "data": [
                            row.get(
                                "avg_review_score",
                                0,
                            )
                            for row in data
                        ],
                    },
                ],
            }

    # ==========================================================
    # Fallback
    # ==========================================================

    return {
        "chart_type": chart_type,
        "title": "Analytics Result",
        "labels": [
            str(index + 1)
            for index in range(len(data))
        ],
        "datasets": [
            {
                "label": "Value",
                "data": [1 for _ in data],
            }
        ],
    }

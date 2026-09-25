from typing import Any


def build_insight(
    tool_name: str,
    result: dict[str, Any],
) -> str:
    """
    Generate a deterministic one-sentence insight from
    analytics results.
    """

    data = result.get("data", [])

    if not data:
        return "No data was found for the requested query."

    # ---------------------------------------------------------
    # ORDER TRENDS
    # ---------------------------------------------------------
    if tool_name == "order_trends":
        highest = max(
            data,
            key=lambda row: row["revenue"],
        )

        return (
            f"Revenue peaked in {highest['period'][:7]} "
            f"at {highest['revenue']:,.2f}, with "
            f"{highest['order_count']:,} orders."
        )

    # ---------------------------------------------------------
    # PRODUCT PERFORMANCE
    # ---------------------------------------------------------
    if tool_name == "product_performance":
        top = data[0]

        if result.get("sort_by") == "order_count":
            return (
                f"{top['category']} had the highest order volume "
                f"with {top['order_count']:,} orders."
            )

        return (
            f"{top['category']} was the top category by revenue, "
            f"generating {top['revenue']:,.2f}."
        )

    # ---------------------------------------------------------
    # SELLER PERFORMANCE
    # ---------------------------------------------------------
    if tool_name == "seller_performance":
        top = data[0]

        return (
            f"Seller {top['seller_id']} generated the highest "
            f"revenue at {top['revenue']:,.2f}."
        )

    # ---------------------------------------------------------
    # REVIEW ANALYSIS
    # ---------------------------------------------------------
    if tool_name == "review_analysis":
        group_by = result.get("group_by", "score")

        if group_by == "category":
            highest = max(
                data,
                key=lambda row: row["avg_review_score"],
            )

            return (
                f"{highest['category']} had the highest average "
                f"review score at {highest['avg_review_score']:.2f}."
            )

        if group_by == "state":
            highest = max(
                data,
                key=lambda row: row["avg_review_score"],
            )

            return (
                f"{highest['state']} had the highest average "
                f"review score at {highest['avg_review_score']:.2f}."
            )

        highest = max(
            data,
            key=lambda row: row["review_count"],
        )

        return (
            f"{highest['review_score']}-star reviews were the "
            f"largest review group at {highest['percentage']:.2f}%."
        )

    # ---------------------------------------------------------
    # PAYMENT BREAKDOWN
    # ---------------------------------------------------------
    if tool_name == "payment_breakdown":
        top = data[0]

        return (
            f"{top['payment_type']} was the dominant payment method, "
            f"accounting for {top['percentage']:.2f}% of payment value."
        )

    # ---------------------------------------------------------
    # DELIVERY PERFORMANCE
    # ---------------------------------------------------------
    if tool_name == "delivery_performance":
        worst = max(
            data,
            key=lambda row: row["late_percentage"],
        )

        return (
            f"{worst['state']} had the highest late-delivery rate "
            f"at {worst['late_percentage']:.2f}%."
        )

    # ---------------------------------------------------------
    # MULTI-TOOL ANALYSIS
    # ---------------------------------------------------------
    if tool_name == "multi_tool":
        inner_tool = result.get("tool")

        # Top categories by order volume + average review score
        if inner_tool == "category_review_comparison":
            highest = max(
                data,
                key=lambda row: row["avg_review_score"],
            )

            return (
                f"{highest['category']} had the highest average "
                f"review score among the top categories by order "
                f"volume at {highest['avg_review_score']:.2f}."
            )

        # Delivery delay + review score by state
        if inner_tool == "state_delivery_review_comparison":
            highest_late = max(
                data,
                key=lambda row: row["late_percentage"],
            )

            highest_review = max(
                data,
                key=lambda row: row["avg_review_score"],
            )

            return (
                f"{highest_late['state']} had the highest late-delivery "
                f"rate at {highest_late['late_percentage']:.2f}%, while "
                f"{highest_review['state']} had the highest average "
                f"review score at {highest_review['avg_review_score']:.2f}."
            )

    return "The requested analysis was completed successfully."
"""Budget Agent: enforces monthly and per-order spending limits."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from app.settings import get_settings
from database.mysql_connector import MySQLConnector
from utils.logger import get_logger

logger = get_logger(__name__)
AGENT_NAME = "Budget Agent"
COMMITTED_STATUSES = ("Approved", "Shipped", "Delivered")


class BudgetAgent:
    def __init__(self, monthly_limit: Optional[float] = None, max_single_order: Optional[float] = None):
        settings = get_settings()
        self.monthly_limit = float(monthly_limit or settings.get("budget.monthly_limit", 100000))
        self.max_single_order = float(max_single_order or settings.get("budget.max_single_order", self.monthly_limit))

    def spent_this_month(self) -> float:
        month_start = date.today().replace(day=1).isoformat()
        with MySQLConnector() as db:
            row = db.fetch_one(
                "SELECT COALESCE(SUM(total_price), 0) AS spent FROM purchase_orders "
                "WHERE order_status IN (%s, %s, %s) AND created_at >= %s",
                (*COMMITTED_STATUSES, month_start),
            )
        return float((row or {}).get("spent") or 0)

    def remaining_budget(self) -> float:
        return round(self.monthly_limit - self.spent_this_month(), 2)

    def evaluate(self, cost: float, remaining: Optional[float] = None) -> Dict[str, Any]:
        remaining = self.remaining_budget() if remaining is None else remaining
        if cost > self.max_single_order:
            result = {"approved": False, "reason": f"exceeds single-order limit of {self.max_single_order:,.0f}"}
        elif cost > remaining:
            result = {"approved": False, "reason": f"exceeds remaining monthly budget of {remaining:,.0f}"}
        else:
            result = {"approved": True, "reason": f"within budget ({remaining - cost:,.0f} left after order)"}
        result.update({"cost": round(cost, 2), "remaining_before": round(remaining, 2)})
        logger.info("%s: %s %.2f – %s", AGENT_NAME, "approved" if result["approved"] else "rejected", cost, result["reason"])
        return result

    def approve_budget(self, cost: float) -> bool:
        return self.evaluate(cost)["approved"]

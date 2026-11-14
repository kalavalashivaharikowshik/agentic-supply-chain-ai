"""Business rules used to resolve conflicts between agents."""

from __future__ import annotations

from typing import Any, Dict

from app.settings import get_settings


class BusinessRules:
    def get_rules(self) -> Dict[str, Any]:
        s = get_settings()
        return {
            "high_risk_priority": True,
            "max_budget": s.get("budget.monthly_limit", 100000),
            "max_single_order": s.get("budget.max_single_order", 60000),
            "critical_stock_days": s.get("inventory.critical_stock_days", 5),
        }

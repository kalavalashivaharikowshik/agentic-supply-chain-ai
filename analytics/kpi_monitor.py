"""Supply chain KPIs computed from live data."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.mysql_connector import MySQLConnector

SEVERITY_WEIGHT = {"LOW": 1, "MEDIUM": 3, "HIGH": 6, "CRITICAL": 10}


class KPIMonitor:
    # ---- pure helpers (unit-testable) ----
    def resilience_score(self, disruptions: int | List[Dict[str, Any]], stock_alerts: int = 0) -> int:
        """100 minus penalties for active disruptions (weighted by level) and stock alerts."""
        if isinstance(disruptions, int):
            penalty = disruptions * 5
        else:
            penalty = sum(SEVERITY_WEIGHT.get(d.get("risk_level", "LOW"), 1) for d in disruptions)
        return int(max(0, min(100, 100 - penalty - stock_alerts * 4)))

    def supplier_score(self, reliability: float) -> float:
        return round(float(reliability) * 100, 1)

    def shipping_delay_avg(self, delays: List[float]) -> float:
        return round(sum(delays) / len(delays), 2) if delays else 0.0

    # ---- live KPIs ----
    def compute_all(self, budget_limit: Optional[float] = None) -> Dict[str, Any]:
        from agents.budget_agent import BudgetAgent
        from agents.inventory_agent import InventoryAgent

        with MySQLConnector() as db:
            risks = db.fetch_all("SELECT risk_level FROM risk_events WHERE status = 'Active'")
            delays = db.fetch_all("SELECT delay_days FROM shipments WHERE status <> 'Delivered'")
            rel = db.fetch_one("SELECT AVG(reliability_score) AS r FROM suppliers WHERE is_active = 1")
            orders = db.fetch_one(
                "SELECT COUNT(*) AS n FROM purchase_orders WHERE order_status IN ('Pending Approval','Approved')"
            )
            delayed = db.fetch_one(
                "SELECT COUNT(*) AS n FROM shipments WHERE status IN ('Delayed','Customs Hold')"
            )
        inventory = InventoryAgent().check_inventory(log=False)
        alerts = [i for i in inventory if i["status"] != "OK"]
        budget = BudgetAgent(monthly_limit=budget_limit)
        spent = budget.spent_this_month()
        covers = [i["days_of_cover"] for i in inventory if i["days_of_cover"] is not None]
        return {
            "resilience_score": self.resilience_score(risks, len(alerts)),
            "avg_shipping_delay": self.shipping_delay_avg([float(d["delay_days"]) for d in delays]),
            "supplier_reliability": self.supplier_score((rel or {}).get("r") or 0),
            "active_risks": len(risks),
            "stock_alerts": len(alerts),
            "delayed_shipments": int((delayed or {}).get("n") or 0),
            "active_shipments": len(delays),
            "open_orders": int((orders or {}).get("n") or 0),
            "budget_used_pct": round(spent / budget.monthly_limit * 100, 1) if budget.monthly_limit else 0.0,
            "budget_remaining": round(budget.monthly_limit - spent, 2),
            "min_days_of_cover": min(covers) if covers else None,
        }

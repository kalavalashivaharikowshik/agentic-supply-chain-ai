"""Procurement Agent: picks suppliers and sizes replenishment orders (risk-aware)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from explainability.decision_explainer import DecisionExplainer
from procurement.cost_optimizer import CostOptimizer
from procurement.supplier_discovery import SupplierDiscovery
from procurement.supplier_ranking import SupplierRanking
from utils.logger import get_logger

logger = get_logger(__name__)
AGENT_NAME = "Procurement Agent"
HIGH_RISK_LEVELS = ("HIGH", "CRITICAL")


class ProcurementAgent:
    def __init__(self):
        self.discovery = SupplierDiscovery()
        self.ranking = SupplierRanking()
        self.optimizer = CostOptimizer()
        self.explainer = DecisionExplainer()

    @staticmethod
    def risky_locations(risks: Optional[List[Dict[str, Any]]]) -> set:
        from utils.constants import PORT_COUNTRY

        locations = set()
        for r in risks or []:
            if r.get("risk_level") in HIGH_RISK_LEVELS:
                locations.add(r["location"])
                if PORT_COUNTRY.get(r["location"]):
                    locations.add(PORT_COUNTRY[r["location"]])
        return locations

    def rank(self, category: Optional[str] = None, risks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Rank suppliers, pushing those in high-risk locations to the bottom."""
        ranked = self.ranking.rank_suppliers(self.discovery.get_suppliers(category))
        risky = self.risky_locations(risks)
        for s in ranked:
            s["at_risk_location"] = s["country"] in risky
        return sorted(ranked, key=lambda s: (s["at_risk_location"], -s["score"]))

    def find_best_supplier(self, category: Optional[str] = None,
                           risks: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        ranked = self.rank(category, risks)
        if not ranked:
            logger.info("%s: no suppliers found for %s", AGENT_NAME, category or "any category")
            return None
        best = ranked[0]
        logger.info("%s: best supplier %s (score %s)", AGENT_NAME, best["supplier_name"], best["score"])
        return best

    def plan_order(self, item: Dict[str, Any], risks: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """Build a purchase plan for an inventory alert produced by the Inventory Agent."""
        ranked = self.rank(item["category"], risks)
        if not ranked:
            return None
        best = ranked[0]
        quantity = self.optimizer.order_quantity(
            current_stock=int(item["stock_quantity"]),
            daily_usage=int(item["daily_usage"]),
            in_transit=int(item.get("in_transit", 0)) + int(item.get("on_order", 0)),
            lead_time_days=int(best["average_lead_time"]),
            capacity=int(best.get("capacity_per_month") or 0) or None,
        )
        if quantity <= 0:
            return None
        total = self.optimizer.calculate_cost(best["price_index"], quantity)
        return {
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "days_of_cover": item.get("days_of_cover"),
            "stock_status": item.get("status"),
            "supplier": best,
            "supplier_id": best["supplier_id"],
            "supplier_name": best["supplier_name"],
            "quantity": quantity,
            "unit_price": float(best["price_index"]),
            "total_cost": total,
            "explanation": self.explainer.explain_supplier_choice(best, ranked[1:]),
            "alternatives": [
                {"supplier_name": s["supplier_name"], "score": s["score"], "price_index": s["price_index"]}
                for s in ranked[1:4]
            ],
        }

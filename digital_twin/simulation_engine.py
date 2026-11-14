"""Digital twin: what-if simulations over the live inventory and supplier data."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.mysql_connector import MySQLConnector
from digital_twin.disruption_models import DisruptionModels
from digital_twin.impact_analyzer import PRODUCTION_RISK, ImpactAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)

INVENTORY_QUERY = (
    "SELECT p.product_id, p.product_name, p.category, p.unit_price, p.daily_usage, "
    "COALESCE(SUM(i.stock_quantity), 0) AS stock_quantity "
    "FROM products p LEFT JOIN inventory i ON i.product_id = p.product_id "
    "GROUP BY p.product_id, p.product_name, p.category, p.unit_price, p.daily_usage"
)


class SimulationEngine:
    def __init__(self):
        self.models = DisruptionModels()
        self.analyzer = ImpactAnalyzer()

    def _inventory(self) -> List[Dict[str, Any]]:
        with MySQLConnector() as db:
            return db.fetch_all(INVENTORY_QUERY)

    def _summarize(self, disruption: Dict[str, Any], products: List[Dict[str, Any]]) -> Dict[str, Any]:
        impacts = []
        for p in products:
            impact = self.analyzer.analyze_delay(p["stock_quantity"], p["daily_usage"],
                                                 disruption["delay_days"], p["unit_price"])
            impacts.append({"product_id": p["product_id"], "product_name": p["product_name"],
                            "stock_quantity": p["stock_quantity"], **impact})
        at_risk = [i for i in impacts if i["status"] == PRODUCTION_RISK]
        overall = PRODUCTION_RISK if at_risk else ("At Risk" if any(i["status"] == "At Risk" for i in impacts) else "No Risk")
        result = {
            "disruption": disruption,
            "overall_status": overall,
            "products_at_risk": len(at_risk),
            "total_revenue_at_risk": round(sum(i["revenue_at_risk"] for i in impacts), 2),
            "impacts": impacts,
        }
        logger.info("Simulation %s (%s days): %s, %d product(s) at risk",
                    disruption["type"], disruption["delay_days"], overall, len(at_risk))
        return result

    def run_delay_simulation(self, delay_days: int, product_id: Optional[int] = None) -> Dict[str, Any]:
        """All inbound supply delayed by ``delay_days``."""
        products = self._inventory()
        if product_id is not None:
            products = [p for p in products if p["product_id"] == product_id]
        return self._summarize(self.models.shipment_delay(delay_days), products)

    def simulate_supplier_failure(self, supplier_id: int, duration_days: int = 30) -> Dict[str, Any]:
        """A supplier stops delivering; only its product category is affected."""
        with MySQLConnector() as db:
            supplier = db.fetch_one("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        if not supplier:
            raise ValueError(f"supplier {supplier_id} not found")
        products = [p for p in self._inventory() if p["category"] == supplier["product_category"]]
        result = self._summarize(self.models.supplier_failure(supplier_id, duration_days), products)
        result["supplier_name"] = supplier["supplier_name"]
        return result

    def simulate_port_closure(self, port_name: str, duration_days: int) -> Dict[str, Any]:
        """Products with shipments routed through ``port_name`` are delayed."""
        with MySQLConnector() as db:
            rows = db.fetch_all(
                "SELECT DISTINCT product_id FROM shipments WHERE status <> 'Delivered' "
                "AND (origin_port = %s OR destination_port = %s)",
                (port_name, port_name),
            )
        affected = {r["product_id"] for r in rows}
        products = [p for p in self._inventory() if p["product_id"] in affected]
        return self._summarize(self.models.port_closure(port_name, duration_days), products)

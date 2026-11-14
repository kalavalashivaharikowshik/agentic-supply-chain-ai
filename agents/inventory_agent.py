"""Inventory Agent: computes days of cover and flags stockout risk."""

from __future__ import annotations

from typing import Any, Dict, List

from app.settings import get_settings
from database.mysql_connector import MySQLConnector
from forecasting.inventory_forecast import InventoryForecast
from utils.helpers import log_decision

AGENT_NAME = "Inventory Agent"

STOCK_QUERY = (
    "SELECT p.product_id, p.product_name, p.category, p.unit_price, p.daily_usage, p.reorder_point, "
    "COALESCE((SELECT SUM(i.stock_quantity) FROM inventory i WHERE i.product_id = p.product_id), 0) AS stock_quantity, "
    "COALESCE((SELECT SUM(s.quantity) FROM shipments s WHERE s.product_id = p.product_id "
    "          AND s.status <> 'Delivered'), 0) AS in_transit, "
    "COALESCE((SELECT SUM(o.quantity) FROM purchase_orders o WHERE o.product_id = p.product_id "
    "          AND o.order_status IN ('Pending Approval', 'Approved')), 0) AS on_order "
    "FROM products p ORDER BY p.product_id"
)


class InventoryAgent:
    def __init__(self):
        settings = get_settings()
        self.critical_days = settings.get("inventory.critical_stock_days", 5)
        self.warning_days = settings.get("inventory.warning_stock_days", 10)
        self.forecast = InventoryForecast()

    def classify(self, days_of_cover) -> str:
        if days_of_cover is None:
            return "OK"
        if days_of_cover <= self.critical_days:
            return "CRITICAL"
        if days_of_cover <= self.warning_days:
            return "LOW"
        return "OK"

    def check_inventory(self, log: bool = True) -> List[Dict[str, Any]]:
        """Return every product with stock, pipeline and stockout status."""
        with MySQLConnector() as db:
            items = db.fetch_all(STOCK_QUERY)
            for item in items:
                days = self.forecast.predict_stockout(item["stock_quantity"], item["daily_usage"])
                item["days_of_cover"] = days
                item["status"] = self.classify(days)
            alerts = [i for i in items if i["status"] != "OK"]
            if log:
                if alerts:
                    summary = "; ".join(f"{a['product_name']} {a['days_of_cover']}d ({a['status']})" for a in alerts)
                    log_decision(AGENT_NAME, "Stock Alert", f"Low cover: {summary}", db)
                else:
                    log_decision(AGENT_NAME, "Stock Check", "All products above warning cover", db)
        return items

    def get_alerts(self) -> List[Dict[str, Any]]:
        return [i for i in self.check_inventory() if i["status"] != "OK"]

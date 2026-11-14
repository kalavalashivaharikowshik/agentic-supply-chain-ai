"""Natural-language Q&A over the supply chain data.

Intent detection is keyword based and answers come straight from the live
database, so responses are always grounded in current data.
"""

from __future__ import annotations

import re
from typing import Callable, List, Optional, Tuple

from analytics.kpi_monitor import KPIMonitor
from database.mysql_connector import MySQLConnector
from knowledge_graph.graph_queries import GraphQueries


class QueryEngine:
    def __init__(self):
        self.intents: List[Tuple[Tuple[str, ...], Callable[[str], str]]] = [
            (("help", "what can you"), self._help),
            (("supplier", "supplies", "vendor", "sourcing", "provide"), self._suppliers),
            (("stock", "inventory", "stockout", "cover"), self._inventory),
            (("risk", "disruption", "alert", "threat"), self._risks),
            (("delay", "shipment", "ship", "vessel", "eta", "track"), self._shipments),
            (("order", "purchase", "po "), self._orders),
            (("budget", "spend", "kpi", "resilience", "health", "summary", "status"), self._kpis),
        ]

    def ask(self, question: str) -> str:
        q = (question or "").lower().strip()
        if not q:
            return self._help(q)
        for keywords, handler in self.intents:
            if any(k in q for k in keywords):
                return handler(q)
        return "I couldn't understand that question. " + self._help(q)

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _stem(word: str) -> str:
        if word.endswith("ies"):
            return word[:-3] + "y"
        if word.endswith("s") and not word.endswith("ss"):
            return word[:-1]
        return word

    def _find_product(self, q: str) -> Optional[str]:
        words = {self._stem(w) for w in re.findall(r"[a-z]+", q)}
        with MySQLConnector() as db:
            products = db.fetch_all("SELECT product_name, category FROM products")
        for p in products:
            for name in (p["product_name"], p["category"]):
                tokens = [self._stem(t) for t in re.findall(r"[a-z]+", name.lower())]
                if tokens and tokens[0] in words:
                    return p["product_name"]
        return None

    # ------------------------------------------------------------ intents
    def _help(self, q: str) -> str:
        return ("Try asking: 'Which suppliers provide semiconductors?', 'What is low on stock?', "
                "'Show active risks', 'Any delayed shipments?', 'Show open purchase orders', "
                "or 'How healthy is the supply chain?'")

    def _suppliers(self, q: str) -> str:
        product = self._find_product(q)
        if product:
            names = GraphQueries().get_suppliers_for_product(product)
            if not names:
                return f"No suppliers found for {product}."
            return f"Suppliers for {product} (most reliable first): " + ", ".join(names)
        with MySQLConnector() as db:
            rows = db.fetch_all("SELECT supplier_name, country, reliability_score FROM suppliers "
                                "WHERE is_active = 1 ORDER BY reliability_score DESC LIMIT 5")
        return "Top suppliers by reliability: " + "; ".join(
            f"{r['supplier_name']} ({r['country']}, {float(r['reliability_score']):.0%})" for r in rows)

    def _inventory(self, q: str) -> str:
        from agents.inventory_agent import InventoryAgent

        items = InventoryAgent().check_inventory(log=False)
        product = self._find_product(q)
        if product:
            items = [i for i in items if i["product_name"] == product]
        else:
            alerts = [i for i in items if i["status"] != "OK"]
            if not alerts:
                return "All products have healthy stock cover."
            items = alerts
        return "\n".join(
            f"{i['product_name']}: {int(i['stock_quantity'])} units, {i['days_of_cover']} days of cover "
            f"({i['status']}), {int(i['in_transit'])} in transit" for i in items)

    def _risks(self, q: str) -> str:
        with MySQLConnector() as db:
            rows = db.fetch_all("SELECT event_type, location, severity_score, risk_level FROM risk_events "
                                "WHERE status = 'Active' ORDER BY severity_score DESC LIMIT 5")
        if not rows:
            return "No active supply chain risks."
        return "Active risks:\n" + "\n".join(
            f"• {r['event_type']} at {r['location']} – severity {r['severity_score']} ({r['risk_level']})" for r in rows)

    def _shipments(self, q: str) -> str:
        with MySQLConnector() as db:
            if "delay" in q:
                rows = db.fetch_all("SELECT * FROM shipments WHERE status IN ('Delayed','Customs Hold') "
                                    "OR delay_days > 0 ORDER BY delay_days DESC")
                if not rows:
                    return "No delayed shipments right now."
            else:
                rows = db.fetch_all("SELECT * FROM shipments WHERE status <> 'Delivered' ORDER BY eta")
        return "\n".join(
            f"• {r['vessel_name']}: {r['origin_port']} → {r['destination_port']}, {r['status']}, "
            f"{float(r['progress']):.0%} complete, delay {r['delay_days']}d, ETA {r['eta']}" for r in rows) or "No shipments."

    def _orders(self, q: str) -> str:
        with MySQLConnector() as db:
            rows = db.fetch_all(
                "SELECT o.order_id, o.quantity, o.total_price, o.order_status, p.product_name, s.supplier_name "
                "FROM purchase_orders o JOIN products p ON p.product_id = o.product_id "
                "JOIN suppliers s ON s.supplier_id = o.supplier_id ORDER BY o.order_id DESC LIMIT 8")
        if not rows:
            return "No purchase orders yet."
        return "Recent purchase orders:\n" + "\n".join(
            f"• PO #{r['order_id']}: {r['quantity']} x {r['product_name']} from {r['supplier_name']}, "
            f"{float(r['total_price']):,.2f} ({r['order_status']})" for r in rows)

    def _kpis(self, q: str) -> str:
        k = KPIMonitor().compute_all()
        return (f"Resilience score {k['resilience_score']}/100 · {k['active_risks']} active risk(s) · "
                f"{k['stock_alerts']} stock alert(s) · {k['delayed_shipments']} delayed shipment(s) · "
                f"avg delay {k['avg_shipping_delay']} days · supplier reliability {k['supplier_reliability']}% · "
                f"budget used {k['budget_used_pct']}% ({k['budget_remaining']:,.0f} remaining)")

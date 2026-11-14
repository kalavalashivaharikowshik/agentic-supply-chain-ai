"""Shipment status provider.

Reads shipment state from the database and estimates delay risk from the
recorded delay and any active risk events at the origin/destination ports.
Swap this for a real carrier API (e.g. MarineTraffic, project44) in production.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from database.mysql_connector import MySQLConnector


class ShippingAPI:
    def get_shipment_status(self, shipment_id: int) -> Optional[Dict[str, Any]]:
        with MySQLConnector() as db:
            shipment = db.fetch_one("SELECT * FROM shipments WHERE shipment_id = %s", (shipment_id,))
            if not shipment:
                return None
            risk = db.fetch_one(
                "SELECT MAX(severity_score) AS s FROM risk_events "
                "WHERE status = 'Active' AND location IN (%s, %s)",
                (shipment["origin_port"], shipment["destination_port"]),
            )
        port_risk = (risk or {}).get("s") or 0
        delay_risk = min(100, int(shipment["delay_days"]) * 12 + int(port_risk * 0.6))
        if shipment["status"] in ("Customs Hold", "Delayed"):
            delay_risk = max(delay_risk, 50)
        if shipment["status"] == "Delivered":
            delay_risk = 0
        return {
            "shipment_id": shipment_id,
            "vessel_name": shipment["vessel_name"],
            "status": shipment["status"],
            "progress": shipment["progress"],
            "delay_days": shipment["delay_days"],
            "eta": shipment["eta"],
            "delay_risk": delay_risk,
        }

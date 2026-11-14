"""Port congestion estimate based on inbound traffic and active risk events."""

from __future__ import annotations

from typing import Any, Dict

from database.mysql_connector import MySQLConnector


class PortMonitor:
    def check_port_status(self, port_name: str) -> Dict[str, Any]:
        with MySQLConnector() as db:
            inbound = db.fetch_one(
                "SELECT COUNT(*) AS n FROM shipments WHERE destination_port = %s AND status <> 'Delivered'",
                (port_name,),
            )
            risk = db.fetch_one(
                "SELECT MAX(severity_score) AS s FROM risk_events WHERE status = 'Active' AND location = %s",
                (port_name,),
            )
        inbound_n = int((inbound or {}).get("n") or 0)
        risk_score = int((risk or {}).get("s") or 0)
        congestion = min(100, inbound_n * 15 + risk_score)
        if congestion > 70:
            status = "HIGH CONGESTION"
        elif congestion > 40:
            status = "MEDIUM CONGESTION"
        else:
            status = "NORMAL"
        return {
            "port": port_name,
            "congestion_score": congestion,
            "inbound_shipments": inbound_n,
            "status": status,
        }

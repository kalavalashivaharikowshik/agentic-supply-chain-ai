"""Logistics Agent: watches shipments and port congestion."""

from __future__ import annotations

from typing import Any, Dict

from logistics.port_monitor import PortMonitor
from logistics.shipment_tracker import ShipmentTracker
from utils.helpers import log_decision

AGENT_NAME = "Logistics Agent"


class LogisticsAgent:
    def __init__(self):
        self.tracker = ShipmentTracker()
        self.ports = PortMonitor()

    def monitor_logistics(self) -> Dict[str, Any]:
        shipments = self.tracker.check_shipments()
        destinations = sorted({s["destination_port"] for s in self.tracker.get_active_shipments()})
        port_status = [self.ports.check_port_status(p) for p in destinations]
        at_risk = [s for s in shipments if s["delay_risk"] >= 50]
        congested = [p for p in port_status if p["status"] != "NORMAL"]
        if at_risk or congested:
            parts = [f"{s['vessel_name']} delay risk {s['delay_risk']}" for s in at_risk]
            parts += [f"{p['port']} {p['status'].lower()}" for p in congested]
            log_decision(AGENT_NAME, "Logistics Alert", "; ".join(parts))
        return {"shipments": shipments, "ports": port_status, "at_risk_shipments": at_risk}

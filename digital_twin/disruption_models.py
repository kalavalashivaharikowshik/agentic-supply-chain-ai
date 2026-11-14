"""Disruption scenario definitions used by the digital twin."""

from __future__ import annotations

from typing import Any, Dict


class DisruptionModels:
    def shipment_delay(self, delay_days: int) -> Dict[str, Any]:
        return {"type": "Shipment Delay", "delay_days": int(delay_days)}

    def supplier_failure(self, supplier_id: int, duration_days: int = 30) -> Dict[str, Any]:
        return {"type": "Supplier Failure", "supplier_id": supplier_id, "delay_days": int(duration_days)}

    def port_closure(self, port_name: str, duration_days: int) -> Dict[str, Any]:
        return {"type": "Port Closure", "port": port_name, "delay_days": int(duration_days)}

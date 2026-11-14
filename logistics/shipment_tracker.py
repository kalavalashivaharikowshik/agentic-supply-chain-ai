"""Tracks shipments and moves vessels along their routes."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from api_connectors.shipping_api import ShippingAPI
from database.mysql_connector import MySQLConnector
from utils.constants import PORT_COORDS
from utils.logger import get_logger

logger = get_logger(__name__)


def interpolate_position(origin: str, destination: str, progress: float) -> Tuple[float, float]:
    """Approximate vessel position as a straight line between two ports."""
    o = PORT_COORDS.get(origin, (0.0, 0.0))
    d = PORT_COORDS.get(destination, (0.0, 0.0))
    p = max(0.0, min(1.0, float(progress)))
    lon_diff = d[1] - o[1]
    # take the shorter way around the globe
    if lon_diff > 180:
        lon_diff -= 360
    elif lon_diff < -180:
        lon_diff += 360
    lon = o[1] + lon_diff * p
    lon = ((lon + 180) % 360) - 180
    return (o[0] + (d[0] - o[0]) * p, lon)


class ShipmentTracker:
    def __init__(self, api: ShippingAPI | None = None):
        self.api = api or ShippingAPI()

    def get_active_shipments(self) -> List[Dict[str, Any]]:
        with MySQLConnector() as db:
            rows = db.fetch_all(
                "SELECT s.*, p.product_name, sp.supplier_name FROM shipments s "
                "JOIN products p ON p.product_id = s.product_id "
                "JOIN suppliers sp ON sp.supplier_id = s.supplier_id "
                "WHERE s.status <> 'Delivered' ORDER BY s.shipment_id"
            )
        for row in rows:
            row["lat"], row["lon"] = interpolate_position(row["origin_port"], row["destination_port"], row["progress"])
        return rows

    def check_shipments(self) -> List[Dict[str, Any]]:
        """Return status + delay risk for every active shipment."""
        results = []
        for shipment in self.get_active_shipments():
            status = self.api.get_shipment_status(shipment["shipment_id"])
            if status:
                results.append(status)
                logger.info("Shipment %s (%s): %s, delay risk %s", status["shipment_id"],
                            status["vessel_name"], status["status"], status["delay_risk"])
        return results

    def advance_shipments(self, step: float = 0.05) -> int:
        """Move vessels forward. Delayed / held vessels move at half speed. Returns #delivered."""
        delivered = 0
        with MySQLConnector() as db:
            for s in db.fetch_all("SELECT * FROM shipments WHERE status <> 'Delivered'"):
                speed = step / 2 if s["status"] in ("Delayed", "Customs Hold") else step
                progress = min(1.0, float(s["progress"]) + speed)
                status = s["status"]
                if progress >= 1.0:
                    status = "Delivered"
                    delivered += 1
                    db.execute_query(
                        "UPDATE inventory SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                        (s["quantity"], s["product_id"]),
                    )
                db.execute_query(
                    "UPDATE shipments SET progress = %s, status = %s WHERE shipment_id = %s",
                    (round(progress, 3), status, s["shipment_id"]),
                )
        return delivered

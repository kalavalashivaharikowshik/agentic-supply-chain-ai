"""Creates and updates purchase orders."""

from __future__ import annotations

from typing import Optional

from database.mysql_connector import MySQLConnector
from utils.constants import ORDER_STATUSES
from utils.logger import get_logger

logger = get_logger(__name__)


class PurchaseOrderGenerator:
    def create_order(
        self,
        supplier_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
        status: str = "Pending Approval",
    ) -> Optional[int]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if status not in ORDER_STATUSES:
            raise ValueError(f"invalid status {status!r}")
        with MySQLConnector() as db:
            order_id = db.execute_query(
                "INSERT INTO purchase_orders (supplier_id, product_id, quantity, total_price, order_status) "
                "VALUES (%s,%s,%s,%s,%s)",
                (supplier_id, product_id, int(quantity), round(float(total_price), 2), status),
            )
        logger.info("Purchase order %s created (%s units, %.2f, %s)", order_id, quantity, total_price, status)
        return order_id

    def update_status(self, order_id: int, status: str) -> None:
        if status not in ORDER_STATUSES:
            raise ValueError(f"invalid status {status!r}")
        with MySQLConnector() as db:
            db.execute_query("UPDATE purchase_orders SET order_status = %s WHERE order_id = %s", (status, order_id))

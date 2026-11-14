"""Supplier master data access."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.mysql_connector import MySQLConnector


class SupplierAPI:
    def get_all_suppliers(self) -> List[Dict[str, Any]]:
        with MySQLConnector() as db:
            return db.fetch_all("SELECT * FROM suppliers ORDER BY supplier_id")

    def get_supplier(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        with MySQLConnector() as db:
            return db.fetch_one("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))

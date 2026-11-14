"""Finds active suppliers, optionally filtered by product category."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.mysql_connector import MySQLConnector


class SupplierDiscovery:
    def get_suppliers(self, category: Optional[str] = None, exclude_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM suppliers WHERE is_active = 1"
        params: list = []
        if category:
            query += " AND product_category = %s"
            params.append(category)
        with MySQLConnector() as db:
            suppliers = db.fetch_all(query, params)
        if exclude_ids:
            suppliers = [s for s in suppliers if s["supplier_id"] not in exclude_ids]
        return suppliers

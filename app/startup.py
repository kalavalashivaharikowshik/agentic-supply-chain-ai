"""Startup check: verifies the database connection and prints a data summary."""

from __future__ import annotations

import sys

from database.mysql_connector import MySQLConnector

TABLES = ["suppliers", "products", "inventory", "shipments", "risk_events", "purchase_orders", "agent_decisions"]


def test_connection() -> bool:
    with MySQLConnector() as db:
        if not db.is_connected:
            print("❌ Database connection failed")
            return False
        print(f"✅ Connected ({db.backend})")
        for table in TABLES:
            row = db.fetch_one(f"SELECT COUNT(*) AS n FROM {table}")
            print(f"   {table:<16} {row['n'] if row else 0} rows")
    return True


if __name__ == "__main__":
    sys.exit(0 if test_connection() else 1)

"""Creates the database schema and loads demo seed data."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from database.mysql_connector import MySQLConnector

logger = get_logger(__name__)

DB_DIR = Path(__file__).resolve().parent
TABLES = [
    "agent_decisions",
    "purchase_orders",
    "risk_events",
    "shipments",
    "inventory",
    "products",
    "suppliers",
]


class DataLoader:
    def __init__(self, db: "MySQLConnector"):
        self.db = db

    def _schema_file(self) -> Path:
        return DB_DIR / ("schema_sqlite.sql" if self.db.backend == "sqlite" else "schema.sql")

    def create_schema(self) -> None:
        self.db.execute_script(self._schema_file().read_text(encoding="utf-8"))

    def is_seeded(self) -> bool:
        row = self.db.fetch_one("SELECT COUNT(*) AS n FROM suppliers")
        return bool(row and row["n"])

    def seed(self) -> None:
        self.db.execute_script((DB_DIR / "seed.sql").read_text(encoding="utf-8"))
        logger.info("Seed data loaded")

    def initialize(self, seed: bool = True) -> None:
        """Create tables if needed and seed them when empty."""
        self.create_schema()
        if seed and not self.is_seeded():
            self.seed()

    def reset(self) -> None:
        """Drop all tables and rebuild with fresh seed data."""
        for table in TABLES:
            self.db.execute_query(f"DROP TABLE IF EXISTS {table}")
        self.initialize(seed=True)
        logger.info("Database reset complete")

"""Knowledge graph queries, with an SQL fallback when Neo4j is not available."""

from __future__ import annotations

from typing import Any, Dict, List

from database.mysql_connector import MySQLConnector
from knowledge_graph.neo4j_connector import Neo4jConnector, Neo4jUnavailable
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphQueries:
    def get_suppliers_for_product(self, product_name: str) -> List[str]:
        try:
            with Neo4jConnector() as g:
                rows = g.execute_query(
                    "MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) WHERE toLower(p.name) = toLower($product) "
                    "RETURN s.name AS supplier ORDER BY s.reliability DESC",
                    {"product": product_name},
                )
                if rows:
                    return [r["supplier"] for r in rows]
        except Neo4jUnavailable as exc:
            logger.debug("Graph fallback to SQL: %s", exc)
        with MySQLConnector() as db:
            rows = db.fetch_all(
                "SELECT s.supplier_name FROM suppliers s JOIN products p ON p.category = s.product_category "
                "WHERE LOWER(p.product_name) = LOWER(%s) OR LOWER(p.category) = LOWER(%s) "
                "ORDER BY s.reliability_score DESC",
                (product_name, product_name),
            )
        return list(dict.fromkeys(r["supplier_name"] for r in rows))

    def get_exposure_by_country(self) -> List[Dict[str, Any]]:
        """How many products depend on suppliers in each country."""
        with MySQLConnector() as db:
            return db.fetch_all(
                "SELECT s.country, COUNT(DISTINCT p.product_id) AS products, COUNT(DISTINCT s.supplier_id) AS suppliers "
                "FROM suppliers s JOIN products p ON p.category = s.product_category "
                "GROUP BY s.country ORDER BY products DESC, suppliers DESC"
            )

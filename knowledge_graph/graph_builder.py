"""Builds the supply chain knowledge graph in Neo4j.

Graph model::

    (:Supplier)-[:SUPPLIES]->(:Product)
    (:Supplier)-[:LOCATED_IN]->(:Country)
    (:Shipment)-[:CARRIES]->(:Product), (:Shipment)-[:FROM]->(:Port), (:Shipment)-[:TO]->(:Port)
"""

from __future__ import annotations

from typing import Dict

from database.mysql_connector import MySQLConnector
from knowledge_graph.neo4j_connector import Neo4jConnector
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphBuilder:
    def create_supplier(self, supplier_name: str, country: str | None = None) -> None:
        with Neo4jConnector() as db:
            db.execute_query("MERGE (s:Supplier {name:$name})", {"name": supplier_name})
            if country:
                db.execute_query(
                    "MATCH (s:Supplier {name:$name}) MERGE (c:Country {name:$country}) MERGE (s)-[:LOCATED_IN]->(c)",
                    {"name": supplier_name, "country": country},
                )

    def create_product(self, product_name: str) -> None:
        with Neo4jConnector() as db:
            db.execute_query("MERGE (p:Product {name:$name})", {"name": product_name})

    def create_supply_relation(self, supplier_name: str, product_name: str) -> None:
        with Neo4jConnector() as db:
            db.execute_query(
                "MATCH (s:Supplier {name:$supplier}) MATCH (p:Product {name:$product}) MERGE (s)-[:SUPPLIES]->(p)",
                {"supplier": supplier_name, "product": product_name},
            )

    def sync_from_database(self) -> Dict[str, int]:
        """Mirror suppliers, products and shipments from SQL into Neo4j (idempotent)."""
        with MySQLConnector() as sql:
            suppliers = sql.fetch_all("SELECT * FROM suppliers")
            products = sql.fetch_all("SELECT * FROM products")
            shipments = sql.fetch_all("SELECT s.*, p.product_name FROM shipments s "
                                      "JOIN products p ON p.product_id = s.product_id")
        with Neo4jConnector() as g:
            for p in products:
                g.execute_query("MERGE (p:Product {name:$name}) SET p.category=$cat, p.daily_usage=$usage",
                                {"name": p["product_name"], "cat": p["category"], "usage": p["daily_usage"]})
            for s in suppliers:
                g.execute_query(
                    "MERGE (s:Supplier {name:$name}) SET s.reliability=$rel, s.price=$price, s.lead_time=$lead "
                    "MERGE (c:Country {name:$country}) MERGE (s)-[:LOCATED_IN]->(c) "
                    "WITH s MATCH (p:Product {category:$cat}) MERGE (s)-[:SUPPLIES]->(p)",
                    {"name": s["supplier_name"], "rel": s["reliability_score"], "price": s["price_index"],
                     "lead": s["average_lead_time"], "country": s["country"], "cat": s["product_category"]},
                )
            for sh in shipments:
                g.execute_query(
                    "MERGE (v:Shipment {id:$id}) SET v.vessel=$vessel, v.status=$status "
                    "MERGE (o:Port {name:$origin}) MERGE (d:Port {name:$dest}) "
                    "MERGE (v)-[:FROM]->(o) MERGE (v)-[:TO]->(d) "
                    "WITH v MATCH (p:Product {name:$product}) MERGE (v)-[:CARRIES]->(p)",
                    {"id": sh["shipment_id"], "vessel": sh["vessel_name"], "status": sh["status"],
                     "origin": sh["origin_port"], "dest": sh["destination_port"], "product": sh["product_name"]},
                )
        counts = {"suppliers": len(suppliers), "products": len(products), "shipments": len(shipments)}
        logger.info("Knowledge graph synced: %s", counts)
        return counts

"""Tests for knowledge graph components (SQL fallback when Neo4j is absent)."""

import pytest

from knowledge_graph.graph_queries import GraphQueries
from knowledge_graph.neo4j_connector import Neo4jConnector, Neo4jUnavailable


def test_neo4j_unconfigured_raises_clean_error():
    with pytest.raises(Neo4jUnavailable):
        Neo4jConnector()
    assert Neo4jConnector.is_available() is False


def test_suppliers_for_product_falls_back_to_sql():
    suppliers = GraphQueries().get_suppliers_for_product("Semiconductor")
    assert suppliers[0] == "ABC Microchips"  # most reliable first
    assert len(suppliers) == 4
    assert GraphQueries().get_suppliers_for_product("battery pack")[0] == "Nordic Cell Systems"


def test_exposure_by_country():
    rows = GraphQueries().get_exposure_by_country()
    countries = {r["country"] for r in rows}
    assert {"China", "Germany", "India"} <= countries

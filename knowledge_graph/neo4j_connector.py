"""Neo4j connection (optional). Configure NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jUnavailable(RuntimeError):
    pass


class Neo4jConnector:
    def __init__(self):
        settings = get_settings()
        self.uri = settings.neo4j_uri
        self.username = settings.neo4j_user
        self.password = settings.neo4j_password
        if not self.uri or not self.password:
            raise Neo4jUnavailable("Neo4j is not configured (set NEO4J_URI and NEO4J_PASSWORD)")
        try:
            from neo4j import GraphDatabase

            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self.driver.verify_connectivity()
        except Exception as exc:
            raise Neo4jUnavailable(f"Cannot connect to Neo4j at {self.uri}: {exc}") from exc

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def close(self) -> None:
        self.driver.close()

    def __enter__(self) -> "Neo4jConnector":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @staticmethod
    def is_available() -> bool:
        try:
            Neo4jConnector().close()
            return True
        except Neo4jUnavailable:
            return False

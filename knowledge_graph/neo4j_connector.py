from neo4j import GraphDatabase


class Neo4jConnector:

    def __init__(self):
        self.uri = "neo4j://127.0.0.1:7687"
        self.username = "neo4j"
        self.password = "kowshik123"

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def execute_query(self, query, params=None):

        with self.driver.session() as session:

            result = session.run(query, params if params else {})

            # Convert result to list BEFORE session closes
            records = [record.data() for record in result]

            return records

    def close(self):
        self.driver.close()
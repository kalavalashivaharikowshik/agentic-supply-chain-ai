from knowledge_graph.neo4j_connector import Neo4jConnector


class GraphBuilder:

    def create_supplier(self, supplier_name):

        db = Neo4jConnector()

        query = """
        MERGE (s:Supplier {name:$name})
        """

        db.execute_query(query, {"name": supplier_name})

        db.close()

    def create_product(self, product_name):

        db = Neo4jConnector()

        query = """
        MERGE (p:Product {name:$name})
        """

        db.execute_query(query, {"name": product_name})

        db.close()

    def create_supply_relation(self, supplier_name, product_name):

        db = Neo4jConnector()

        query = """
        MATCH (s:Supplier {name:$supplier})
        MATCH (p:Product {name:$product})
        MERGE (s)-[:SUPPLIES]->(p)
        """

        db.execute_query(query, {
            "supplier": supplier_name,
            "product": product_name
        })

        db.close()
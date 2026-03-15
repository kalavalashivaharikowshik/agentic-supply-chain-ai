from knowledge_graph.neo4j_connector import Neo4jConnector


class GraphQueries:

    def get_suppliers_for_product(self, product_name):

        db = Neo4jConnector()

        query = """
        MATCH (s:Supplier)-[:SUPPLIES]->(p:Product {name:$product})
        RETURN s.name AS supplier
        """

        result = db.execute_query(query, {"product": product_name})

        suppliers = [record["supplier"] for record in result]

        db.close()

        return suppliers
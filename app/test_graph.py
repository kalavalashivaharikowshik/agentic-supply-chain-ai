from knowledge_graph.graph_builder import GraphBuilder
from knowledge_graph.graph_queries import GraphQueries


def run():

    builder = GraphBuilder()

    builder.create_supplier("ABC Microchips")
    builder.create_product("Semiconductor")
    builder.create_supply_relation("ABC Microchips", "Semiconductor")

    queries = GraphQueries()

    suppliers = queries.get_suppliers_for_product("Semiconductor")

    print("Suppliers for Semiconductor:", suppliers)


if __name__ == "__main__":
    run()
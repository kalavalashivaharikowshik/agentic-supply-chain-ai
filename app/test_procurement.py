from procurement.supplier_discovery import SupplierDiscovery
from procurement.supplier_ranking import SupplierRanking
from procurement.cost_optimizer import CostOptimizer
from procurement.purchase_order_generator import PurchaseOrderGenerator


def run():

    discovery = SupplierDiscovery()
    suppliers = discovery.get_suppliers()

    ranking = SupplierRanking()
    ranked = ranking.rank_suppliers(suppliers)

    if not ranked:
        print("No suppliers found")
        return

    best_supplier = ranked[0]

    optimizer = CostOptimizer()
    cost = optimizer.calculate_cost(best_supplier["price_index"], 100)

    order = PurchaseOrderGenerator()
    order.create_order(best_supplier["supplier_id"], 1, 100, cost)

    print("Best Supplier:", best_supplier["supplier_name"])


if __name__ == "__main__":
    run()
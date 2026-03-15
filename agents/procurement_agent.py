from procurement.supplier_discovery import SupplierDiscovery
from procurement.supplier_ranking import SupplierRanking


class ProcurementAgent:

    def find_best_supplier(self):

        discovery = SupplierDiscovery()
        suppliers = discovery.get_suppliers()

        ranking = SupplierRanking()

        ranked = ranking.rank_suppliers(suppliers)

        if ranked:
            best = ranked[0]

            print("Procurement Agent → Best Supplier:", best["supplier_name"])

            return best

        print("Procurement Agent → No suppliers found")
        return None
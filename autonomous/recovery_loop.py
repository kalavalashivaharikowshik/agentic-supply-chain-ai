from risk_analysis.disruption_detector import DisruptionDetector
from digital_twin.simulation_engine import SimulationEngine
from agents.procurement_agent import ProcurementAgent
from procurement.purchase_order_generator import PurchaseOrderGenerator


class RecoveryLoop:

    def run(self):

        print("Detecting disruption")

        DisruptionDetector().detect_disruptions()

        print("Running simulation")

        impact = SimulationEngine().run_delay_simulation(10)

        if impact == "Production Risk":

            supplier = ProcurementAgent().find_best_supplier()

            PurchaseOrderGenerator().create_order(
                supplier["supplier_id"],
                1,
                100,
                supplier["price_index"]*100
            )

            print("Recovery action executed")
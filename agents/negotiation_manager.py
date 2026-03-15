from agents.inventory_agent import InventoryAgent
from agents.procurement_agent import ProcurementAgent
from agents.budget_agent import BudgetAgent


class NegotiationManager:

    def run_negotiation(self):

        inventory_agent = InventoryAgent()
        inventory_agent.check_inventory()

        procurement_agent = ProcurementAgent()
        supplier = procurement_agent.find_best_supplier()

        if supplier:

            estimated_cost = supplier["price_index"] * 100

            budget = BudgetAgent()

            approved = budget.approve_budget(estimated_cost)

            if approved:
                print("Negotiation Manager → Procurement Approved")
            else:
                print("Negotiation Manager → Procurement Blocked")
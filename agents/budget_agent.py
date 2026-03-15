class BudgetAgent:

    def approve_budget(self, cost):

        budget_limit = 100000

        if cost <= budget_limit:

            print("Budget Agent → Budget Approved")

            return True

        print("Budget Agent → Budget Rejected")

        return False
from conflict_resolver.business_rules import BusinessRules


class RuleEngine:

    def evaluate(self, stock_days, cost, risk_level):

        rules = BusinessRules().get_rules()

        if stock_days <= rules["critical_stock_days"]:

            return "URGENT_PROCUREMENT"

        if cost > rules["max_budget"]:

            return "REJECT_COST"

        if risk_level == "CRITICAL":

            return "RISK_MITIGATION"

        return "NORMAL_OPERATION"
class DecisionExplainer:

    def explain_supplier_choice(self,supplier):

        return f"""
        Recommended Supplier: {supplier['supplier_name']}

        Reasons:
        • Reliability score high
        • Competitive price
        • Faster lead time
        """
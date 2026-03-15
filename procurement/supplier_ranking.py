class SupplierRanking:

    def rank_suppliers(self, suppliers):

        if not suppliers:
            return []

        ranked = sorted(
            suppliers,
            key=lambda x: (
                -float(x["reliability_score"]),   # higher reliability first
                float(x["price_index"]),          # lower price next
                int(x["average_lead_time"])       # shorter lead time
            )
        )

        return ranked
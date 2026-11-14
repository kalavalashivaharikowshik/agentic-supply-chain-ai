"""Chooses a transport mode based on urgency and cost."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Indicative per-shipment cost multipliers and transit times
TRANSPORT_MODES: List[Dict[str, Any]] = [
    {"mode": "Sea Freight", "transit_days": 25, "cost_per_unit": 0.8},
    {"mode": "Rail Transport", "transit_days": 15, "cost_per_unit": 1.6},
    {"mode": "Air Freight", "transit_days": 3, "cost_per_unit": 6.0},
]


class RouteOptimizer:
    def recommend(self, quantity: int, deadline_days: float, budget: Optional[float] = None) -> Dict[str, Any]:
        """Cheapest mode that arrives before ``deadline_days`` (and within budget).

        Falls back to the fastest mode when nothing meets the deadline.
        """
        options = []
        for m in TRANSPORT_MODES:
            cost = round(m["cost_per_unit"] * quantity, 2)
            options.append({**m, "cost": cost, "meets_deadline": m["transit_days"] <= deadline_days})
        feasible = [o for o in options if o["meets_deadline"] and (budget is None or o["cost"] <= budget)]
        if feasible:
            choice = min(feasible, key=lambda o: o["cost"])
        else:
            choice = min(options, key=lambda o: o["transit_days"])
        return {**choice, "alternatives": options}

    def choose_route(self, cost: float, time: float) -> str:
        """Backwards-compatible helper: ``time`` is the deadline in days, ``cost`` the budget."""
        if time < 3:
            return "Air Freight"
        return self.recommend(quantity=1000, deadline_days=time, budget=cost)["mode"]

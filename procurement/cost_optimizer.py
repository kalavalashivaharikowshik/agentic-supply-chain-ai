"""Order sizing and cost calculation."""

from __future__ import annotations

import math

from app.settings import get_settings


class CostOptimizer:
    def calculate_cost(self, unit_price: float, quantity: int) -> float:
        return round(float(unit_price) * int(quantity), 2)

    def order_quantity(
        self,
        current_stock: int,
        daily_usage: int,
        in_transit: int = 0,
        lead_time_days: int = 0,
        capacity: int | None = None,
        lot_size: int = 50,
    ) -> int:
        """Units needed to reach the target days of cover after the lead time.

        Covers consumption during the supplier lead time plus
        ``inventory.target_cover_days`` of stock, minus what is on hand and in
        transit. Rounded up to ``lot_size`` and capped at supplier capacity.
        """
        target_days = get_settings().get("inventory.target_cover_days", 30)
        needed = daily_usage * (target_days + lead_time_days) - current_stock - in_transit
        if needed <= 0:
            return 0
        qty = int(math.ceil(needed / lot_size) * lot_size)
        if capacity:
            qty = min(qty, int(capacity))
        return qty

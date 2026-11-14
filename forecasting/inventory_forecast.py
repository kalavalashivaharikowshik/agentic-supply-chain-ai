"""Days-of-cover / stockout estimation."""

from __future__ import annotations

from typing import Optional, Sequence


class InventoryForecast:
    def predict_stockout(self, current_stock: float, daily_usage: float) -> Optional[float]:
        """Days until stock runs out at a constant usage rate (None if no usage)."""
        if not daily_usage or daily_usage <= 0:
            return None
        return round(max(0.0, float(current_stock)) / float(daily_usage), 2)

    def predict_stockout_from_forecast(self, current_stock: float, forecast: Sequence[float]) -> Optional[int]:
        """Day index on which forecast demand exhausts stock (None if it never does)."""
        remaining = float(current_stock)
        for day, demand in enumerate(forecast, start=1):
            remaining -= float(demand)
            if remaining <= 0:
                return day
        return None

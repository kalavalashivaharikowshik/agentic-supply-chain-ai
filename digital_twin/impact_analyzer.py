"""Quantifies the impact of a supply delay on a product's inventory."""

from __future__ import annotations

from typing import Any, Dict

NO_RISK = "No Risk"
AT_RISK = "At Risk"
PRODUCTION_RISK = "Production Risk"


class ImpactAnalyzer:
    def analyze_delay(self, current_stock: float, daily_usage: float, delay_days: float,
                      unit_price: float = 0.0, buffer_days: float = 3) -> Dict[str, Any]:
        """Compare days of cover against the delay.

        * ``Production Risk`` – stock runs out before the delayed supply arrives
        * ``At Risk``         – stock lasts, but with less than ``buffer_days`` margin
        * ``No Risk``         – comfortable cover
        """
        if not daily_usage or daily_usage <= 0:
            return {"status": NO_RISK, "days_of_cover": None, "shortfall_days": 0,
                    "shortfall_units": 0, "revenue_at_risk": 0.0}
        cover = float(current_stock) / float(daily_usage)
        shortfall_days = max(0.0, float(delay_days) - cover)
        shortfall_units = int(round(shortfall_days * daily_usage))
        if shortfall_days > 0:
            status = PRODUCTION_RISK
        elif cover - delay_days < buffer_days:
            status = AT_RISK
        else:
            status = NO_RISK
        return {
            "status": status,
            "days_of_cover": round(cover, 1),
            "shortfall_days": round(shortfall_days, 1),
            "shortfall_units": shortfall_units,
            "revenue_at_risk": round(shortfall_units * float(unit_price), 2),
        }

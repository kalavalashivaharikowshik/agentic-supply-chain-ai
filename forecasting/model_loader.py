"""Provides the forecasting models used by the agents."""

from __future__ import annotations

from typing import Any, Dict

from forecasting.demand_forecast import DemandForecast
from forecasting.inventory_forecast import InventoryForecast


class ModelLoader:
    def load_models(self) -> Dict[str, Any]:
        return {"demand_model": DemandForecast(), "inventory_model": InventoryForecast()}

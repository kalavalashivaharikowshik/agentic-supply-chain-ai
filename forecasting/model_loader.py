from forecasting.demand_forecast import DemandForecast
from forecasting.inventory_forecast import InventoryForecast


class ModelLoader:

    def load_models(self):

        demand_model = DemandForecast()
        inventory_model = InventoryForecast()

        return {
            "demand_model": demand_model,
            "inventory_model": inventory_model
        }
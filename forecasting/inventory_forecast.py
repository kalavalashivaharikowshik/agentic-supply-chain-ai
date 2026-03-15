class InventoryForecast:

    def predict_stockout(self, current_stock, daily_usage):

        if daily_usage == 0:
            return "No consumption data"

        days_remaining = current_stock / daily_usage

        return round(days_remaining, 2)
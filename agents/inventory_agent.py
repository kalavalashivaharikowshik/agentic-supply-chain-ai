from forecasting.inventory_forecast import InventoryForecast
from database.mysql_connector import MySQLConnector


class InventoryAgent:

    def check_inventory(self):

        db = MySQLConnector()
        db.connect()

        inventory = db.fetch_all("SELECT * FROM inventory")

        forecast = InventoryForecast()

        for item in inventory:

            days_left = forecast.predict_stockout(
                item["stock_quantity"],
                100
            )

            print(
                "Inventory Agent → Product",
                item["product_id"],
                "Stockout in",
                days_left,
                "days"
            )

        db.close()
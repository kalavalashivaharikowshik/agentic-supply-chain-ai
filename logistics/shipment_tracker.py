from api_connectors.shipping_api import ShippingAPI
from database.mysql_connector import MySQLConnector


class ShipmentTracker:

    def check_shipments(self):

        db = MySQLConnector()
        db.connect()

        shipments = db.fetch_all("SELECT * FROM shipments")

        shipping_api = ShippingAPI()

        for shipment in shipments:

            shipment_id = shipment["shipment_id"]

            status_data = shipping_api.get_shipment_status(shipment_id)

            print("Shipment:", shipment_id, "| Status:", status_data["status"])

        db.close()
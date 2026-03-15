import random


class ShippingAPI:

    def get_shipment_status(self, shipment_id):

        statuses = [
            "In Transit",
            "Delayed",
            "At Port",
            "Customs Hold",
            "Delivered"
        ]

        return {
            "shipment_id": shipment_id,
            "status": random.choice(statuses),
            "delay_risk": random.randint(0, 100)
        }
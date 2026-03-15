class DisruptionModels:

    def shipment_delay(self, delay_days):

        return {
            "type": "Shipment Delay",
            "delay_days": delay_days
        }

    def supplier_failure(self, supplier_id):

        return {
            "type": "Supplier Failure",
            "supplier_id": supplier_id
        }
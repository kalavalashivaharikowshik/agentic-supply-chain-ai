from logistics.shipment_tracker import ShipmentTracker
from logistics.port_monitor import PortMonitor


class LogisticsAgent:

    def monitor_logistics(self):

        tracker = ShipmentTracker()
        tracker.check_shipments()

        port = PortMonitor()
        status = port.check_port_status("Shanghai Port")

        print("Logistics Agent → Port Status:", status)
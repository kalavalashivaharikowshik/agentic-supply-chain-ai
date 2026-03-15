from logistics.shipment_tracker import ShipmentTracker
from logistics.port_monitor import PortMonitor


def run():

    tracker = ShipmentTracker()
    tracker.check_shipments()

    port = PortMonitor()
    port_status = port.check_port_status("Shanghai Port")

    print("\nPort Status:")
    print(port_status)


if __name__ == "__main__":
    run()
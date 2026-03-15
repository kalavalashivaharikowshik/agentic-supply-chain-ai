import random


class PortMonitor:

    def check_port_status(self, port_name):

        congestion_level = random.randint(0, 100)

        if congestion_level > 70:
            status = "HIGH CONGESTION"
        elif congestion_level > 40:
            status = "MEDIUM CONGESTION"
        else:
            status = "NORMAL"

        return {
            "port": port_name,
            "congestion_score": congestion_level,
            "status": status
        }
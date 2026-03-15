from database.mysql_connector import MySQLConnector


class RiskAgent:

    def check_risks(self):

        db = MySQLConnector()
        db.connect()

        events = db.fetch_all("SELECT * FROM risk_events")

        for event in events:

            print(
                "Risk Agent → Event:",
                event["event_type"],
                "| Severity:",
                event["severity_score"]
            )

        db.close()
from risk_analysis.weather_monitor import WeatherMonitor
from risk_analysis.news_sentiment import NewsSentiment
from risk_analysis.risk_scorer import RiskScorer
from database.mysql_connector import MySQLConnector


class DisruptionDetector:

    def detect_disruptions(self):

        events = []

        weather = WeatherMonitor()
        weather_event = weather.check_weather_risk(31.2304, 121.4737)

        if weather_event:
            events.append(weather_event)

        news = NewsSentiment()
        news_events = news.analyze_news()

        events.extend(news_events)

        scorer = RiskScorer()

        db = MySQLConnector()
        db.connect()

        for event in events:

            risk_level = scorer.calculate_risk(event["severity_score"])

            query = """
            INSERT INTO risk_events (event_type, location, severity_score, detected_by)
            VALUES (%s,%s,%s,%s)
            """

            db.execute_query(query, (
                event["event_type"],
                "Global",
                event["severity_score"],
                "Risk Engine"
            ))

            print("Risk detected:", event["event_type"], "| Level:", risk_level)

        db.close()
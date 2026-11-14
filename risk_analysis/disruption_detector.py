"""Collects disruption signals (weather, news) and records them as risk events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.mysql_connector import MySQLConnector
from risk_analysis.news_sentiment import NewsSentiment
from risk_analysis.risk_scorer import RiskScorer
from risk_analysis.weather_monitor import WeatherMonitor
from utils.logger import get_logger

logger = get_logger(__name__)


class DisruptionDetector:
    def __init__(self, weather: Optional[WeatherMonitor] = None, news: Optional[NewsSentiment] = None):
        self.weather = weather or WeatherMonitor()
        self.news = news or NewsSentiment()
        self.scorer = RiskScorer()

    def collect_signals(self) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        events.extend(self.weather.check_all_ports())
        events.extend(self.news.analyze_news())
        return events

    def record_event(self, db: MySQLConnector, event: Dict[str, Any], detected_by: str = "Risk Engine") -> Optional[int]:
        """Insert an event unless an identical active one already exists."""
        level = event.get("risk_level") or self.scorer.calculate_risk(event["severity_score"])
        existing = db.fetch_one(
            "SELECT event_id FROM risk_events WHERE status = 'Active' AND event_type = %s "
            "AND location = %s AND COALESCE(description, '') = %s",
            (event["event_type"], event.get("location", "Global"), event.get("description") or ""),
        )
        if existing:
            return None
        return db.execute_query(
            "INSERT INTO risk_events (event_type, location, severity_score, risk_level, description, detected_by) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (
                event["event_type"],
                event.get("location", "Global"),
                int(event["severity_score"]),
                level,
                event.get("description"),
                detected_by,
            ),
        )

    def detect_disruptions(self, persist: bool = True) -> List[Dict[str, Any]]:
        events = self.collect_signals()
        if persist and events:
            with MySQLConnector() as db:
                for event in events:
                    self.record_event(db, event)
        for event in events:
            logger.info("Risk detected: %s @ %s | %s", event["event_type"], event.get("location"), event["risk_level"])
        return events

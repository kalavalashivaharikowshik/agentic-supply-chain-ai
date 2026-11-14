"""Risk Agent: monitors active disruption events."""

from __future__ import annotations

from typing import Any, Dict, List

from database.mysql_connector import MySQLConnector
from risk_analysis.disruption_detector import DisruptionDetector
from risk_analysis.risk_scorer import RiskScorer
from utils.helpers import log_decision

AGENT_NAME = "Risk Agent"


class RiskAgent:
    def __init__(self):
        self.scorer = RiskScorer()

    def scan_external_sources(self) -> List[Dict[str, Any]]:
        """Pull fresh weather/news signals into the risk_events table."""
        return DisruptionDetector().detect_disruptions(persist=True)

    def check_risks(self, scan_external: bool = False, log: bool = True) -> List[Dict[str, Any]]:
        """Return active risk events (highest severity first)."""
        if scan_external:
            self.scan_external_sources()
        with MySQLConnector() as db:
            events = db.fetch_all(
                "SELECT * FROM risk_events WHERE status = 'Active' ORDER BY severity_score DESC, event_id DESC"
            )
            for e in events:
                e["risk_level"] = self.scorer.calculate_risk(e["severity_score"])
            if events and log:
                top = events[0]
                log_decision(
                    AGENT_NAME,
                    "Risk Assessment",
                    f"{len(events)} active risk(s); highest: {top['event_type']} at {top['location']} "
                    f"(severity {top['severity_score']}, {top['risk_level']})",
                    db,
                )
        return events

    def resolve_risk(self, event_id: int) -> None:
        with MySQLConnector() as db:
            db.execute_query("UPDATE risk_events SET status = 'Resolved' WHERE event_id = %s", (event_id,))
            log_decision(AGENT_NAME, "Risk Resolved", f"Risk event {event_id} marked resolved", db)

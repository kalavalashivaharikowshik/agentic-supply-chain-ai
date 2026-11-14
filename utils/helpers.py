"""Small shared helpers."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


def generate_id() -> str:
    """Return a short unique identifier."""
    return uuid.uuid4().hex[:10]


def calculate_risk_score(value: float) -> str:
    """Map a 0-100 severity score to a risk level (uses config thresholds)."""
    from risk_analysis.risk_scorer import RiskScorer

    return RiskScorer().calculate_risk(value)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def log_decision(agent_name: str, decision_type: str, description: str, db: Optional[Any] = None) -> None:
    """Persist an agent decision to the audit table (agent_decisions)."""
    from database.mysql_connector import MySQLConnector

    logger.info("%s | %s | %s", agent_name, decision_type, description)
    owns_db = db is None
    db = db or MySQLConnector()
    try:
        db.execute_query(
            "INSERT INTO agent_decisions (agent_name, decision_type, decision_description) VALUES (%s,%s,%s)",
            (agent_name, decision_type, description[:1000]),
        )
    except Exception as exc:  # never let audit logging break an agent
        logger.warning("Could not record decision: %s", exc)
    finally:
        if owns_db:
            db.close()

"""Applies the rule engine and records the outcome."""

from __future__ import annotations

from typing import Optional

from conflict_resolver.rule_engine import RuleEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class DecisionMaker:
    def __init__(self):
        self.engine = RuleEngine()

    def make_decision(self, stock_days, cost, risk_level, budget_available: Optional[float] = None) -> str:
        result = self.engine.evaluate_detailed(stock_days, cost, risk_level, budget_available)
        logger.info("Decision Maker → %s (%s)", result["decision"], "; ".join(result["reasons"]))
        return result["decision"]

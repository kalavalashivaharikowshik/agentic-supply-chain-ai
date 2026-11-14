"""Autonomous recovery loop: detect → simulate → act.

1. Scan external sources for disruptions (weather / news).
2. Run a digital-twin delay simulation sized to the worst active risk.
3. If any product faces a production risk, run the multi-agent cycle, which
   places replenishment orders with the safest suitable suppliers.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from agents.risk_agent import RiskAgent
from digital_twin.impact_analyzer import PRODUCTION_RISK
from digital_twin.simulation_engine import SimulationEngine
from orchestrator.agent_graph import run_agent_cycle
from utils.helpers import log_decision
from utils.logger import get_logger

logger = get_logger(__name__)

# expected supply delay (days) for each risk level
DELAY_BY_LEVEL = {"LOW": 2, "MEDIUM": 5, "HIGH": 10, "CRITICAL": 20}


class RecoveryLoop:
    def __init__(self, scan_external: bool = True, auto_execute: bool = True):
        self.scan_external = scan_external
        self.auto_execute = auto_execute

    def run(self, delay_days: Optional[int] = None) -> Dict[str, Any]:
        risks = RiskAgent().check_risks(scan_external=self.scan_external)
        if delay_days is None:
            levels = [r["risk_level"] for r in risks] or ["LOW"]
            delay_days = max(DELAY_BY_LEVEL.get(lv, 2) for lv in levels)

        simulation = SimulationEngine().run_delay_simulation(delay_days)
        result: Dict[str, Any] = {"risks": len(risks), "delay_days": delay_days,
                                  "simulation": simulation, "cycle": None}

        if simulation["overall_status"] == PRODUCTION_RISK:
            at_risk = [i["product_name"] for i in simulation["impacts"] if i["status"] == PRODUCTION_RISK]
            log_decision("Recovery Loop", "Disruption Response",
                         f"{delay_days}-day delay would stop production of {', '.join(at_risk)}; triggering agents")
            result["cycle"] = run_agent_cycle(auto_execute=self.auto_execute)
        else:
            log_decision("Recovery Loop", "Disruption Response",
                         f"{delay_days}-day delay simulated: {simulation['overall_status']}, no action needed")
        return result

    def run_forever(self, interval_seconds: int = 900) -> None:  # pragma: no cover
        while True:
            try:
                self.run()
            except Exception as exc:
                logger.exception("Recovery loop iteration failed: %s", exc)
            time.sleep(interval_seconds)

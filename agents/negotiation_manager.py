"""Negotiation Manager: runs the full multi-agent decision cycle."""

from __future__ import annotations

from typing import Any, Dict


class NegotiationManager:
    def run_negotiation(self, auto_execute: bool = True) -> Dict[str, Any]:
        from orchestrator.agent_graph import run_agent_cycle

        return run_agent_cycle(auto_execute=auto_execute)

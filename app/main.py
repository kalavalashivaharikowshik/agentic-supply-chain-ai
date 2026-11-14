"""Command-line entry point.

Examples::

    python -m app.main init-db [--reset]
    python -m app.main run-agents [--dry-run] [--scan]
    python -m app.main recover [--delay 10] [--no-scan]
    python -m app.main detect-risks
    python -m app.main simulate --delay 12
    python -m app.main simulate --supplier 1 --delay 20
    python -m app.main simulate --port "Busan Port" --delay 7
    python -m app.main forecast 100 120 110 130 140 --periods 7
    python -m app.main ask "Which suppliers provide semiconductors?"
    python -m app.main kpis
    python -m app.main sync-graph
    python -m app.main dashboard
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _print_json(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def cmd_init_db(args) -> None:
    from database.data_loader import DataLoader
    from database.mysql_connector import MySQLConnector

    with MySQLConnector(auto_init=False) as db:
        if not db.is_connected:
            sys.exit("Could not connect to the database")
        loader = DataLoader(db)
        loader.reset() if args.reset else loader.initialize()
        print(f"Database ready ({db.backend})")


def cmd_run_agents(args) -> None:
    from orchestrator.agent_graph import run_agent_cycle

    state = run_agent_cycle(auto_execute=not args.dry_run, scan_external=args.scan)
    print(state.get("summary", ""))


def cmd_recover(args) -> None:
    from autonomous.recovery_loop import RecoveryLoop

    result = RecoveryLoop(scan_external=not args.no_scan).run(delay_days=args.delay)
    print(f"Simulated {result['delay_days']}-day delay → {result['simulation']['overall_status']}")
    if result["cycle"]:
        print(result["cycle"].get("summary", ""))
    else:
        print("No recovery action required")


def cmd_detect_risks(args) -> None:
    from agents.risk_agent import RiskAgent

    events = RiskAgent().scan_external_sources()
    print(f"{len(events)} signal(s) detected")
    _print_json(events)


def cmd_simulate(args) -> None:
    from digital_twin.simulation_engine import SimulationEngine

    engine = SimulationEngine()
    if args.supplier:
        result = engine.simulate_supplier_failure(args.supplier, args.delay)
    elif args.port:
        result = engine.simulate_port_closure(args.port, args.delay)
    else:
        result = engine.run_delay_simulation(args.delay)
    _print_json(result)


def cmd_forecast(args) -> None:
    from forecasting.demand_forecast import DemandForecast

    print(DemandForecast().forecast_demand(args.history, args.periods))


def cmd_ask(args) -> None:
    from query_engine import QueryEngine

    print(QueryEngine().ask(" ".join(args.question)))


def cmd_kpis(args) -> None:
    from analytics.kpi_monitor import KPIMonitor

    _print_json(KPIMonitor().compute_all())


def cmd_sync_graph(args) -> None:
    from knowledge_graph.graph_builder import GraphBuilder
    from knowledge_graph.neo4j_connector import Neo4jUnavailable

    try:
        print(GraphBuilder().sync_from_database())
    except Neo4jUnavailable as exc:
        sys.exit(str(exc))


def cmd_dashboard(args) -> None:
    script = os.path.join(PROJECT_ROOT, "control_tower", "dashboard.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", script, "--server.port", str(args.port)], check=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="supply-chain-ai", description="Agentic AI Supply Chain Control Tower")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-db", help="create tables and load demo data")
    p.add_argument("--reset", action="store_true", help="drop and recreate all tables")
    p.set_defaults(func=cmd_init_db)

    p = sub.add_parser("run-agents", help="run one multi-agent decision cycle")
    p.add_argument("--dry-run", action="store_true", help="plan only, do not create purchase orders")
    p.add_argument("--scan", action="store_true", help="scan weather/news before deciding")
    p.set_defaults(func=cmd_run_agents)

    p = sub.add_parser("recover", help="autonomous detect → simulate → act loop (one iteration)")
    p.add_argument("--delay", type=int, default=None, help="override simulated delay in days")
    p.add_argument("--no-scan", action="store_true", help="skip external weather/news scan")
    p.set_defaults(func=cmd_recover)

    p = sub.add_parser("detect-risks", help="scan weather and news for disruptions")
    p.set_defaults(func=cmd_detect_risks)

    p = sub.add_parser("simulate", help="digital twin what-if simulation")
    p.add_argument("--delay", type=int, default=10, help="disruption length in days")
    p.add_argument("--supplier", type=int, help="simulate failure of this supplier id")
    p.add_argument("--port", help="simulate closure of this port")
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("forecast", help="forecast demand from a history of daily values")
    p.add_argument("history", nargs="+", type=float)
    p.add_argument("--periods", type=int, default=7)
    p.set_defaults(func=cmd_forecast)

    p = sub.add_parser("ask", help="ask a question in plain English")
    p.add_argument("question", nargs="+")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("kpis", help="print live KPIs")
    p.set_defaults(func=cmd_kpis)

    p = sub.add_parser("sync-graph", help="mirror SQL data into Neo4j")
    p.set_defaults(func=cmd_sync_graph)

    p = sub.add_parser("dashboard", help="launch the Streamlit control tower")
    p.add_argument("--port", type=int, default=8501)
    p.set_defaults(func=cmd_dashboard)
    return parser


NO_DB_COMMANDS = {"init-db", "forecast", "dashboard", "sync-graph"}


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command not in NO_DB_COMMANDS:
        from database.mysql_connector import MySQLConnector

        with MySQLConnector() as db:
            if not db.is_connected:
                sys.exit("Could not connect to the database (check MYSQL* settings or unset MYSQLHOST for SQLite)")
    args.func(args)


if __name__ == "__main__":
    main()

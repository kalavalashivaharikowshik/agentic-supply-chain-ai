"""Agentic AI Supply Chain Control Tower (Streamlit).

Run with:  streamlit run control_tower/dashboard.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st  # noqa: E402

from agents.logistics_agent import LogisticsAgent  # noqa: E402
from agents.risk_agent import RiskAgent  # noqa: E402
from autonomous.recovery_loop import RecoveryLoop  # noqa: E402
from control_tower.agent_chat_view import show_agent_activity, show_assistant  # noqa: E402
from control_tower.kpi_panel import show_kpis  # noqa: E402
from control_tower.procurement_panel import show_procurement  # noqa: E402
from control_tower.risk_panel import show_risks  # noqa: E402
from control_tower.shipment_map import show_supply_chain_map  # noqa: E402
from control_tower.simulation_panel import show_inventory, show_simulation  # noqa: E402
from database.data_loader import DataLoader  # noqa: E402
from database.mysql_connector import MySQLConnector  # noqa: E402
from logistics.shipment_tracker import ShipmentTracker  # noqa: E402
from orchestrator.agent_graph import run_agent_cycle  # noqa: E402
from risk_analysis.disruption_detector import DisruptionDetector  # noqa: E402
from utils.helpers import log_decision  # noqa: E402

SIMULATED_EVENTS = [
    ("Storm Alert", "Shanghai Port", 72, "Typhoon warning; port operations suspended for 48h"),
    ("Port Strike", "Singapore Port", 85, "Dock workers' union announces indefinite strike"),
    ("Supplier Delay", "Taiwan", 66, "Power outage at wafer fab; output reduced 40%"),
    ("Customs Delay", "Rotterdam Port", 55, "New inspection rules causing 3-day clearance backlog"),
    ("Port Congestion", "Los Angeles Port", 60, "Vessel queue above 30 ships"),
    ("Earthquake", "Kaohsiung Port", 90, "M6.8 earthquake; cranes offline pending inspection"),
]


def simulate_event() -> str:
    event_type, location, severity, description = random.choice(SIMULATED_EVENTS)
    detector = DisruptionDetector()
    with MySQLConnector() as db:
        detector.record_event(db, {"event_type": event_type, "location": location,
                                   "severity_score": severity, "description": description},
                              detected_by="Simulator")
        log_decision("Logistics Agent", "Disruption Response",
                     f"Detected {event_type} at {location} (severity {severity})", db)
    return f"{event_type} at {location}"


def sidebar() -> None:
    st.sidebar.header("🕹 Control Panel")
    backend = MySQLConnector(auto_connect=False).backend
    st.sidebar.caption(f"Database: **{backend.upper()}**")

    if st.sidebar.button("🧠 Run Agent Cycle", type="primary", width="stretch"):
        with st.spinner("Agents collaborating..."):
            state = run_agent_cycle(auto_execute=True)
        st.session_state.last_summary = state.get("summary", "")

    if st.sidebar.button("🔁 Autonomous Recovery Loop", width="stretch"):
        with st.spinner("Detect → simulate → act..."):
            result = RecoveryLoop(scan_external=False).run()
        cycle = result.get("cycle")
        st.session_state.last_summary = (
            f"Simulated {result['delay_days']}-day delay: {result['simulation']['overall_status']}\n"
            + (cycle.get("summary", "") if cycle else "No action required")
        )

    if st.sidebar.button("⚡ Simulate Disruption Event", width="stretch"):
        st.sidebar.success(f"Simulated: {simulate_event()}")

    if st.sidebar.button("🛰 Scan Weather & News", width="stretch"):
        with st.spinner("Scanning external sources..."):
            events = RiskAgent().scan_external_sources()
        st.sidebar.info(f"{len(events)} new signal(s) found")

    if st.sidebar.button("🚢 Advance Ships", width="stretch"):
        delivered = ShipmentTracker().advance_shipments()
        LogisticsAgent().monitor_logistics()
        if delivered:
            st.sidebar.success(f"{delivered} shipment(s) delivered; inventory updated")

    st.sidebar.divider()
    if st.sidebar.button("♻ Reset Demo Data", width="stretch"):
        with MySQLConnector() as db:
            DataLoader(db).reset()
        st.session_state.pop("last_summary", None)
        st.session_state.pop("chat", None)
        st.sidebar.success("Demo data restored")


def run_dashboard() -> None:
    st.set_page_config(page_title="AI Supply Chain Control Tower", page_icon="🌍", layout="wide")
    st.title("🌍 Agentic AI Supply Chain Control Tower")

    db = MySQLConnector()
    if not db.is_connected:
        st.error("Database connection failed. Check your MYSQL* environment variables "
                 "or unset MYSQLHOST to use the built-in SQLite database.")
        st.stop()
    db.close()

    sidebar()

    if st.session_state.get("last_summary"):
        st.info("**Last agent cycle**\n\n" + st.session_state.last_summary.replace("\n", "  \n"))

    col1, col2 = st.columns([3, 1])
    with col1:
        show_supply_chain_map()
    with col2:
        show_kpis()

    tabs = st.tabs(["⚠ Risk Monitoring", "🤖 Agent Activity", "📦 Procurement",
                    "🏭 Inventory", "🧪 Digital Twin", "💬 Assistant"])
    with tabs[0]:
        show_risks()
    with tabs[1]:
        show_agent_activity()
    with tabs[2]:
        show_procurement()
    with tabs[3]:
        show_inventory()
    with tabs[4]:
        show_simulation()
    with tabs[5]:
        show_assistant()


if __name__ == "__main__":
    run_dashboard()

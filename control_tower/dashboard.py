import sys
import os
import random
from database.mysql_connector import MySQLConnector


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

from shipment_map import show_supply_chain_map
from risk_panel import show_risks
from procurement_panel import show_procurement
from agent_chat_view import show_agent_activity
from kpi_panel import show_kpis
def run_dashboard():

    st.set_page_config(
        page_title="AI Supply Chain Control Tower",
        layout="wide"
    )

    st.title("🌍 Agentic AI Supply Chain Control Tower")
    
if st.button("⚡ Simulate Supply Chain Event"):

    db = MySQLConnector()

    events = [
        ("Storm Alert", "Shanghai Port", 72),
        ("Port Strike", "Singapore Port", 85),
        ("Supplier Delay", "Taiwan Factory", 66),
        ("Customs Delay", "Rotterdam Port", 55)
    ]

    event = random.choice(events)

   if db.connection:

    cursor = db.connection.cursor()

    cursor.execute(
        "INSERT INTO risk_events (event_type, location, severity_score) VALUES (%s,%s,%s)",
        event
    )

    cursor.execute(
        "INSERT INTO agent_decisions (agent_name, decision_type, decision_description) VALUES (%s,%s,%s)",
        (
            "Logistics Agent",
            "Disruption Response",
            f"Detected {event[0]} at {event[1]}"
        )
    )

    db.connection.commit()

    st.success("Supply chain disruption simulated!")

else:
    st.error("Database connection failed.")

    st.success("Supply chain disruption simulated!")

    if st.button("🔄 Update Ship Positions"):
        st.rerun()

    col1, col2 = st.columns([3,1])

    with col1:
        show_supply_chain_map()

    with col2:
        show_kpis()

    tab1, tab2, tab3 = st.tabs([
        "⚠ Risk Monitoring",
        "🤖 Agent Activity",
        "📦 Procurement"
    ])

    with tab1:
        show_risks()

    with tab2:
        show_agent_activity()

    with tab3:
        show_procurement()


if __name__ == "__main__":
    run_dashboard()

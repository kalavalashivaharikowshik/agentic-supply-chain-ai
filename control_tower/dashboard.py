import sys
import os

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
"""Digital twin what-if simulations and inventory view."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from agents.inventory_agent import InventoryAgent
from database.mysql_connector import MySQLConnector
from digital_twin.simulation_engine import SimulationEngine
from utils.constants import MAJOR_PORTS

STATUS_ICON = {"Production Risk": "🟥", "At Risk": "🟨", "No Risk": "🟩"}


def show_inventory() -> None:
    st.subheader("🏭 Inventory Health")
    items = InventoryAgent().check_inventory(log=False)
    df = pd.DataFrame(items)[["product_name", "stock_quantity", "daily_usage", "days_of_cover",
                              "in_transit", "on_order", "status"]]
    st.dataframe(df, hide_index=True, width="stretch")
    st.bar_chart(df.set_index("product_name")["days_of_cover"], height=220)


def show_simulation() -> None:
    st.subheader("🧪 Digital Twin – What-if Simulation")
    engine = SimulationEngine()
    scenario = st.selectbox("Scenario", ["Shipment delay", "Supplier failure", "Port closure"])
    days = st.slider("Disruption length (days)", 1, 60, 10)

    if scenario == "Supplier failure":
        with MySQLConnector() as db:
            suppliers = db.fetch_all("SELECT supplier_id, supplier_name, product_category FROM suppliers")
        labels = {f"{s['supplier_name']} ({s['product_category']})": s["supplier_id"] for s in suppliers}
        choice = st.selectbox("Supplier", list(labels))
    elif scenario == "Port closure":
        port = st.selectbox("Port", MAJOR_PORTS)

    if st.button("▶ Run simulation", type="primary"):
        if scenario == "Shipment delay":
            result = engine.run_delay_simulation(days)
        elif scenario == "Supplier failure":
            result = engine.simulate_supplier_failure(labels[choice], days)
        else:
            result = engine.simulate_port_closure(port, days)

        icon = STATUS_ICON.get(result["overall_status"], "")
        st.markdown(f"### {icon} {result['overall_status']}")
        c1, c2 = st.columns(2)
        c1.metric("Products at production risk", result["products_at_risk"])
        c2.metric("Revenue at risk", f"{result['total_revenue_at_risk']:,.0f}")
        if result["impacts"]:
            st.dataframe(pd.DataFrame(result["impacts"]), hide_index=True, width="stretch")
        else:
            st.info("No products are affected by this scenario.")

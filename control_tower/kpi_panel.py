"""KPI tiles computed from live data."""

from __future__ import annotations

import streamlit as st

from analytics.kpi_monitor import KPIMonitor


def show_kpis() -> None:
    st.subheader("📊 System KPIs")
    k = KPIMonitor().compute_all()

    c1, c2 = st.columns(2)
    c1.metric("Resilience Score", f"{k['resilience_score']}%")
    c2.metric("Avg Shipping Delay", f"{k['avg_shipping_delay']} days")
    c1.metric("Supplier Reliability", f"{k['supplier_reliability']}%")
    c2.metric("Budget Used", f"{k['budget_used_pct']}%", help=f"{k['budget_remaining']:,.0f} remaining this month")
    c1.metric("Active Risks", k["active_risks"])
    c2.metric("Stock Alerts", k["stock_alerts"])
    c1.metric("Delayed Shipments", f"{k['delayed_shipments']}/{k['active_shipments']}")
    c2.metric("Open Orders", k["open_orders"])
    if k["min_days_of_cover"] is not None:
        st.progress(min(1.0, k["min_days_of_cover"] / 30),
                    text=f"Lowest stock cover: {k['min_days_of_cover']} days")

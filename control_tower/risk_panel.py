"""Risk monitoring panel."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from agents.risk_agent import RiskAgent
from database.mysql_connector import MySQLConnector

ICON = {"CRITICAL": "🟥", "HIGH": "🟧", "MEDIUM": "🟨", "LOW": "🟩"}


def show_risks() -> None:
    st.subheader("⚠ Detected Supply Chain Risks")
    with MySQLConnector() as db:
        events = db.fetch_all("SELECT * FROM risk_events ORDER BY status, severity_score DESC, event_id DESC")

    active = [e for e in events if e["status"] == "Active"]
    if not active:
        st.success("No active risks detected")
    for e in active:
        col1, col2 = st.columns([6, 1])
        col1.markdown(
            f"{ICON.get(e['risk_level'], '⬜')} **{e['event_type']}** at **{e['location']}** — "
            f"severity {e['severity_score']} ({e['risk_level']})  \n"
            f"<small>{e.get('description') or ''} · detected by {e['detected_by']} · {e['detected_at']}</small>",
            unsafe_allow_html=True,
        )
        if col2.button("Resolve", key=f"resolve_{e['event_id']}"):
            RiskAgent().resolve_risk(e["event_id"])
            st.rerun()

    resolved = [e for e in events if e["status"] != "Active"]
    if resolved:
        with st.expander(f"Resolved risks ({len(resolved)})"):
            st.dataframe(pd.DataFrame(resolved)[["event_id", "event_type", "location", "severity_score",
                                                 "risk_level", "detected_at"]],
                         hide_index=True, width="stretch")

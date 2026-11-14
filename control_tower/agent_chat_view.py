"""Agent activity log and natural-language assistant."""

from __future__ import annotations

import streamlit as st

from database.mysql_connector import MySQLConnector
from query_engine import QueryEngine

AGENT_ICON = {
    "Risk Agent": "🛰",
    "Inventory Agent": "📦",
    "Procurement Agent": "🛒",
    "Budget Agent": "💰",
    "Logistics Agent": "🚢",
    "Orchestrator": "🧠",
    "Recovery Loop": "🔁",
}


def show_agent_activity(limit: int = 40) -> None:
    st.subheader("🤖 Agent Activity")
    with MySQLConnector() as db:
        logs = db.fetch_all(
            "SELECT * FROM agent_decisions ORDER BY decision_id DESC LIMIT %s", (limit,)
        )
    if not logs:
        st.info("No agent decisions recorded yet — run an agent cycle from the sidebar.")
        return
    for log in logs:
        icon = AGENT_ICON.get(log["agent_name"], "🤖")
        st.markdown(
            f"{icon} **{log['agent_name']}** · _{log['decision_type']}_ · "
            f"<small>{log['created_at']}</small>  \n{log['decision_description']}",
            unsafe_allow_html=True,
        )


def show_assistant() -> None:
    st.subheader("💬 Ask the Control Tower")
    if "chat" not in st.session_state:
        st.session_state.chat = [("assistant", QueryEngine().ask("help"))]
    for role, text in st.session_state.chat:
        with st.chat_message(role):
            st.text(text) if "\n" in text else st.write(text)
    question = st.chat_input("e.g. Which suppliers provide semiconductors?")
    if question:
        st.session_state.chat.append(("user", question))
        st.session_state.chat.append(("assistant", QueryEngine().ask(question)))
        st.rerun()

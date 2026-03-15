import streamlit as st
from database.mysql_connector import MySQLConnector


def show_agent_activity():

    st.subheader("🤖 Agent Activity")

    db = MySQLConnector()

    logs = db.fetch_all("SELECT * FROM agent_decisions")

    if not logs:
        st.info("No agent decisions recorded")

    else:
        for log in logs:

            st.write(
                f"{log['agent_name']} → {log['decision']}"
            )

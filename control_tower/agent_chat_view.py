import streamlit as st
from database.mysql_connector import MySQLConnector


def show_agent_activity():

    st.subheader("Agent Decisions")

    db = MySQLConnector()
    db.connect()

    decisions = db.fetch_all("SELECT * FROM agent_decisions")

    if not decisions:
        st.info("No agent activity yet")

    else:
        for d in decisions:

            st.write(
                f"{d['agent_name']} → {d['decision_description']}"
            )

    db.close()
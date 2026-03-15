import streamlit as st
from database.mysql_connector import MySQLConnector


def show_risks():

    st.subheader("Detected Supply Chain Risks")

    db = MySQLConnector()
    db.connect()

    events = db.fetch_all("SELECT * FROM risk_events")

    if not events:
        st.info("No risks detected")

    else:
        for event in events:

            st.warning(
                f"{event['event_type']} | Severity: {event['severity_score']}"
            )

    db.close()
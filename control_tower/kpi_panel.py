import streamlit as st


def show_kpis():

    st.subheader("📊 System KPIs")

    col1,col2 = st.columns(2)

    col1.metric(
        "Resilience Score",
        "87%"
    )

    col2.metric(
        "Avg Shipping Delay",
        "2.1 days"
    )

    col1.metric(
        "Supplier Reliability",
        "92%"
    )

    col2.metric(
        "Procurement Cost Variance",
        "+3%"
    )
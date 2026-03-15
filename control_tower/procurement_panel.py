import streamlit as st
from database.mysql_connector import MySQLConnector


def show_procurement():

    st.subheader("Purchase Orders")

    db = MySQLConnector()
    db.connect()

    orders = db.fetch_all("SELECT * FROM purchase_orders")

    if not orders:
        st.info("No purchase orders")

    else:
        for o in orders:

            st.write(
                f"Order {o['order_id']} | Product {o['product_id']} | Qty {o['quantity']} | Status {o['order_status']}"
            )

    db.close()

st.info(
"""
AI Recommendation

Supplier: ABC Microchips

Reason:
• reliability score highest
• delivery faster by 4 days
• price only 2% higher
"""
)
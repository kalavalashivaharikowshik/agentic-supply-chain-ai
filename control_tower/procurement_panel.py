"""Purchase orders and AI supplier recommendations."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from agents.inventory_agent import InventoryAgent
from agents.procurement_agent import ProcurementAgent
from agents.risk_agent import RiskAgent
from database.mysql_connector import MySQLConnector
from procurement.purchase_order_generator import PurchaseOrderGenerator
from utils.helpers import log_decision


def _orders_table() -> None:
    with MySQLConnector() as db:
        orders = db.fetch_all(
            "SELECT o.order_id, p.product_name, s.supplier_name, o.quantity, o.total_price, "
            "o.order_status, o.created_at FROM purchase_orders o "
            "JOIN products p ON p.product_id = o.product_id "
            "JOIN suppliers s ON s.supplier_id = o.supplier_id ORDER BY o.order_id DESC"
        )
    if not orders:
        st.info("No purchase orders yet")
        return

    pending = [o for o in orders if o["order_status"] == "Pending Approval"]
    if pending:
        st.markdown("**Awaiting human approval**")
        gen = PurchaseOrderGenerator()
        for o in pending:
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.write(f"PO #{o['order_id']} · {o['quantity']} x {o['product_name']} from "
                     f"{o['supplier_name']} · {float(o['total_price']):,.2f}")
            if c2.button("Approve", key=f"approve_{o['order_id']}"):
                gen.update_status(o["order_id"], "Approved")
                log_decision("Human Planner", "PO Approval", f"Approved PO #{o['order_id']}")
                st.rerun()
            if c3.button("Reject", key=f"reject_{o['order_id']}"):
                gen.update_status(o["order_id"], "Rejected")
                log_decision("Human Planner", "PO Approval", f"Rejected PO #{o['order_id']}")
                st.rerun()

    df = pd.DataFrame(orders)
    df["total_price"] = df["total_price"].map(lambda v: f"{float(v):,.2f}")
    st.dataframe(df, hide_index=True, width="stretch")


def _recommendations() -> None:
    st.markdown("#### 🧠 AI Recommendations")
    alerts = [i for i in InventoryAgent().check_inventory(log=False) if i["status"] != "OK"]
    if not alerts:
        st.success("All products have healthy stock cover — no purchases recommended.")
        return
    risks = RiskAgent().check_risks(log=False)
    agent = ProcurementAgent()
    for item in alerts:
        plan = agent.plan_order(item, risks)
        title = f"{item['product_name']} — {item['days_of_cover']} days of cover ({item['status']})"
        with st.expander(title, expanded=item["status"] == "CRITICAL"):
            if not plan:
                st.write("Stock in transit / on order already covers the target. No new order needed.")
                continue
            st.write(f"Suggested order: **{plan['quantity']} units** from **{plan['supplier_name']}** "
                     f"at {plan['unit_price']:,.2f} = **{plan['total_cost']:,.2f}**")
            st.text(plan["explanation"])
            if plan["alternatives"]:
                st.caption("Alternatives: " + ", ".join(
                    f"{a['supplier_name']} (score {a['score']})" for a in plan["alternatives"]))


def show_procurement() -> None:
    st.subheader("📦 Procurement")
    _recommendations()
    st.markdown("#### Purchase Orders")
    _orders_table()

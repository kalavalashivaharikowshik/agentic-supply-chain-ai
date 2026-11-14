"""Global map: ports, live vessel positions, routes and active risk zones."""

from __future__ import annotations

import folium
import streamlit as st
from streamlit_folium import st_folium

from database.mysql_connector import MySQLConnector
from logistics.shipment_tracker import ShipmentTracker
from utils.constants import PORT_COORDS, PORTS

LEVEL_COLOR = {"LOW": "#f2c94c", "MEDIUM": "orange", "HIGH": "red", "CRITICAL": "darkred"}
STATUS_COLOR = {"In Transit": "blue", "Delayed": "orange", "Customs Hold": "purple"}


def build_map() -> folium.Map:
    m = folium.Map(location=[25, 60], zoom_start=2, world_copy_jump=True)

    for p in PORTS:
        folium.Marker(
            [p["lat"], p["lon"]],
            tooltip=p["name"],
            icon=folium.Icon(color="green", icon="anchor", prefix="fa"),
        ).add_to(m)

    for s in ShipmentTracker().get_active_shipments():
        origin = PORT_COORDS.get(s["origin_port"])
        if origin:
            folium.PolyLine([origin, (s["lat"], s["lon"])], color="#4a6fa5", weight=2,
                            opacity=0.6, dash_array="6").add_to(m)
        folium.Marker(
            [s["lat"], s["lon"]],
            tooltip=(f"{s['vessel_name']} · {s['product_name']} x{s['quantity']}<br>"
                     f"{s['origin_port']} → {s['destination_port']}<br>"
                     f"{s['status']} · {float(s['progress']):.0%} · ETA {s['eta']}"),
            icon=folium.Icon(color=STATUS_COLOR.get(s["status"], "blue"), icon="ship", prefix="fa"),
        ).add_to(m)

    with MySQLConnector() as db:
        risks = db.fetch_all("SELECT * FROM risk_events WHERE status = 'Active'")
    for r in risks:
        coords = PORT_COORDS.get(r["location"])
        if not coords:
            continue
        folium.Circle(
            location=coords,
            radius=150000 + int(r["severity_score"]) * 6000,
            color=LEVEL_COLOR.get(r["risk_level"], "red"),
            fill=True,
            fill_opacity=0.25,
            popup=f"{r['event_type']} – severity {r['severity_score']} ({r['risk_level']})",
        ).add_to(m)
    return m


def show_supply_chain_map() -> None:
    st.subheader("🌍 Global Supply Chain Map")
    st_folium(build_map(), use_container_width=True, height=520, key="supply_chain_map", returned_objects=[])
    st.caption("🟢 ports · 🔵 in transit · 🟠 delayed · 🟣 customs hold · red circles = active risks")

import streamlit as st
import folium
from streamlit_folium import st_folium
import random


ports = [
    {"name": "Shanghai Port", "lat": 31.23, "lon": 121.47},
    {"name": "Singapore Port", "lat": 1.29, "lon": 103.85},
    {"name": "Rotterdam Port", "lat": 51.92, "lon": 4.48},
]


risk_zones = [
    {"name": "Storm Zone", "lat": 25, "lon": 130},
    {"name": "Port Strike", "lat": 35, "lon": 120},
]


def move_ships():
    for ship in st.session_state.ships:
        ship["lat"] += random.uniform(-0.2, 0.2)
        ship["lon"] += random.uniform(-0.2, 0.2)


def show_supply_chain_map():

    st.subheader("🌍 Global Supply Chain Map")

    # SAFE initialization
    if "ships" not in st.session_state:
        st.session_state.ships = [
            {"name": "Evergreen", "lat": 22, "lon": 120},
            {"name": "Maersk", "lat": 30, "lon": 140},
            {"name": "COSCO", "lat": 10, "lon": 100},
        ]

    move_ships()

    m = folium.Map(location=[20, 0], zoom_start=2)

    # Ports
    for p in ports:
        folium.Marker(
            [p["lat"], p["lon"]],
            tooltip=p["name"],
            icon=folium.Icon(color="green", icon="anchor"),
        ).add_to(m)

    # Ships
    for s in st.session_state.ships:
        folium.Marker(
            [s["lat"], s["lon"]],
            tooltip=s["name"],
            icon=folium.Icon(color="blue", icon="ship"),
        ).add_to(m)

    # Risk zones
    for r in risk_zones:
        folium.Circle(
            location=[r["lat"], r["lon"]],
            radius=500000,
            color="red",
            fill=True,
            fill_opacity=0.3,
            popup=r["name"],
        ).add_to(m)

    st_folium(
        m,
        width=1100,
        height=600,
        key="map_static",
        returned_objects=[]
    )

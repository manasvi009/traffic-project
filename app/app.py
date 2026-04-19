import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Traffic Prediction System", layout="wide")

# 🔥 CHANGE THIS when deploying to AWS
API_URL = "https://traffic-api-0w9r.onrender.com/predict"

# ------------------ TITLE ------------------
st.title("🚦 Smart Traffic Prediction System with Map")

# ------------------ SIDEBAR INPUT ------------------
st.sidebar.header("Enter Trip Details")

start_area = st.sidebar.text_input("Start Area", "Delhi")
end_area = st.sidebar.text_input("End Area", "Noida")

distance = st.sidebar.number_input("Distance (km)", min_value=0.0)
avg_speed = st.sidebar.number_input("Average Speed (km/h)", min_value=1.0)

time_of_day = st.sidebar.slider("Time of Day (0–23)", 0, 23)

day_of_week = st.sidebar.selectbox(
    "Day of Week",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)

weather = st.sidebar.selectbox("Weather", ["Clear","Rainy","Foggy"])
traffic = st.sidebar.selectbox("Traffic Density", ["Low","Medium","High"])
road = st.sidebar.selectbox("Road Type", ["Highway","City","Rural"])

# ------------------ BUTTONS ------------------
col1, col2 = st.columns(2)

predict_clicked = col1.button("🚗 Predict Travel Time")
map_clicked = col2.button("🗺️ Show Route on Map")

# ------------------ PREDICTION ------------------
if predict_clicked:

    data = {
        "start_area": start_area,
        "end_area": end_area,
        "distance_km": distance,
        "average_speed_kmph": avg_speed,
        "time_of_day": time_of_day,
        "day_of_week": day_of_week,
        "weather_condition": weather,
        "traffic_density_level": traffic,
        "road_type": road
    }

    try:
        response = requests.post(API_URL, json=data)

        if response.status_code == 200:
            result = response.json()
            st.success(f"🚗 Estimated Travel Time: {result['travel_time']:.2f} minutes")
        else:
            st.error("❌ API Error")

    except:
        st.error("❌ Could not connect to API. Make sure Flask server is running.")

# ------------------ MAP SECTION ------------------
if map_clicked:

    st.subheader("🗺️ Route Visualization")

    geolocator = Nominatim(user_agent="traffic_app")

    try:
        start_loc = geolocator.geocode(start_area)
        end_loc = geolocator.geocode(end_area)

        if start_loc and end_loc:

            start_coords = [start_loc.latitude, start_loc.longitude]
            end_coords = [end_loc.latitude, end_loc.longitude]

            # Create map centered at midpoint
            mid_lat = (start_coords[0] + end_coords[0]) / 2
            mid_lon = (start_coords[1] + end_coords[1]) / 2

            m = folium.Map(location=[mid_lat, mid_lon], zoom_start=11)

            # Start Marker
            folium.Marker(
                start_coords,
                tooltip="Start",
                icon=folium.Icon(color="green")
            ).add_to(m)

            # End Marker
            folium.Marker(
                end_coords,
                tooltip="End",
                icon=folium.Icon(color="red")
            ).add_to(m)

            # Draw line (route approximation)
            folium.PolyLine(
                [start_coords, end_coords],
                tooltip="Route",
                weight=5
            ).add_to(m)

            # Display map
            st_folium(m, width=900, height=500)

        else:
            st.error("❌ Could not find one or both locations")

    except Exception as e:
        st.error("❌ Error loading map")
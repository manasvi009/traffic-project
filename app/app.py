import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import openrouteservice
import time
import random
import pickle
from folium.plugins import HeatMap
import os

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Traffic Prediction System", layout="wide")

WEATHER_API_KEY = "d624225ef53223f6fa372e4c2d33a2bf"
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijg5NzcwZTI1OGRkNjRiYTE4OGJlNmFmMGE3ODAzOGQ0IiwiaCI6Im11cm11cjY0In0="

# ------------------ LOAD ML MODEL ------------------
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

# ------------------ TITLE ------------------
st.title("🚦 Smart Traffic Prediction System with Live Map")

# ------------------ AUTO REFRESH ------------------
st.caption("🔄 Auto-updating traffic every 5 seconds")

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

if time.time() - st.session_state.last_update > 5:
    st.session_state.last_update = time.time()
    st.rerun()

# ------------------ SIDEBAR ------------------
st.sidebar.header("🚗 Enter Trip Details")

start_area = st.sidebar.text_input("Start Area", "Delhi")
end_area = st.sidebar.text_input("End Area", "Noida")

time_of_day = st.sidebar.slider("Time of Day (0–23)", 0, 23, 10)

road = st.sidebar.selectbox("Road Type", ["Highway","City","Rural"])

predict_btn = st.sidebar.button("🚀 Predict Travel Time")

# ------------------ LIVE TRAFFIC ------------------
def get_live_traffic():
    return random.choice(["Low", "Medium", "High"])

traffic = get_live_traffic()
st.sidebar.write(f"🚦 Live Traffic: {traffic}")

# ------------------ ENCODER ------------------
def encode_inputs(distance, speed, time_of_day, traffic, weather, road):
    traffic_map = {"Low": 1, "Medium": 2, "High": 3}
    weather_map = {"Clear": 0, "Rainy": 1, "Foggy": 1}
    road_map = {"Highway": 1, "City": 2, "Rural": 3}

    return [[
        distance,
        speed,
        time_of_day,
        traffic_map[traffic],
        weather_map[weather],
        road_map[road]
    ]]

# ------------------ GEOLOCATOR ------------------
geolocator = Nominatim(user_agent="traffic_app", timeout=10)

def get_coordinates(place):
    try:
        location = geolocator.geocode(
            place + ", India",
            exactly_one=True
        )

        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return None, None

# ------------------ WEATHER API ------------------
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
        response = requests.get(url).json()

        weather_main = response['weather'][0]['main']

        if weather_main.lower() in ["rain", "drizzle"]:
            return "Rainy"
        elif weather_main.lower() in ["fog", "mist", "haze"]:
            return "Foggy"
        else:
            return "Clear"
    except:
        return "Clear"

# ------------------ TRAFFIC COLOR ------------------
def get_traffic_color(level):
    return {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }.get(level, "blue")

# ------------------ ROUTE FUNCTION ------------------
def get_route(start, end):
    try:
        client = openrouteservice.Client(key=ORS_API_KEY)

        route = client.directions(
            coordinates=[start, end],
            profile='driving-car',
            format='geojson'   # 🔥 IMPORTANT LINE
        )

        # Now geometry has coordinates
        coords = route['features'][0]['geometry']['coordinates']

        # Convert (lon, lat) → (lat, lon)
        return [(c[1], c[0]) for c in coords]

    except Exception as e:
        st.error(f"Route Error: {e}")
        return None
# ------------------ DISTANCE FUNCTION ------------------
def calculate_distance(route_coords):
    total = 0
    for i in range(len(route_coords) - 1):
        lat1, lon1 = route_coords[i]
        lat2, lon2 = route_coords[i+1]
        total += ((lat2 - lat1)**2 + (lon2 - lon1)**2) ** 0.5

    return total * 111

# ------------------ MAIN ------------------
if start_area and end_area:

    src_lat, src_lon = get_coordinates(start_area)
    dst_lat, dst_lon = get_coordinates(end_area)

    if src_lat and dst_lat:

        weather = get_weather(src_lat, src_lon)
        st.sidebar.write(f"🌦️ Live Weather: {weather}")

        # Map
        mid_lat = (src_lat + dst_lat) / 2
        mid_lon = (src_lon + dst_lon) / 2

        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)

        # Markers
        folium.Marker([src_lat, src_lon], tooltip="Start",
                      icon=folium.Icon(color="green")).add_to(m)

        folium.Marker([dst_lat, dst_lon], tooltip="Destination",
                      icon=folium.Icon(color="red")).add_to(m)

        route_coords = get_route((src_lon, src_lat), (dst_lon, dst_lat))

        if route_coords:

            # ✅ CALCULATE DISTANCE HERE
            distance = calculate_distance(route_coords)

            # -------- ROUTE --------
            for i in range(len(route_coords) - 1):
                segment_traffic = random.choice(["Low", "Medium", "High"])
                color = get_traffic_color(segment_traffic)

                folium.PolyLine(
                    [route_coords[i], route_coords[i + 1]],
                    color=color,
                    weight=6
                ).add_to(m)

            # -------- VEHICLE --------
            vehicle_position = random.choice(route_coords)

            folium.Marker(
                location=vehicle_position,
                tooltip="🚗 Live Vehicle",
                icon=folium.Icon(color="blue")
            ).add_to(m)

            # -------- HEATMAP --------
            heat_data = [[c[0], c[1], random.uniform(0.2, 1.0)] for c in route_coords]
            HeatMap(heat_data).add_to(m)

            # -------- PREDICTION --------
            if predict_btn:
                input_data = encode_inputs(
                    distance,
                    40,
                    time_of_day,
                    traffic,
                    weather,
                    road
                )

                prediction = model.predict(input_data)[0]
                st.success(f"🚗 Estimated Travel Time: {prediction:.2f} minutes")

        else:
            st.warning("⚠️ Route not found")

        st_folium(m, width=900, height=500)

    else:
        st.warning("⚠️ Enter valid locations")

else:
    st.info("ℹ️ Please enter start and destination")
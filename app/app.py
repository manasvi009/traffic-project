import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Traffic Prediction System", layout="wide")

API_URL = "https://traffic-api-0w9r.onrender.com/predict"
WEATHER_API_KEY = "198a7b515a67010cd0cc212227bc7255"

# ------------------ TITLE ------------------
st.title("🚦 Smart Traffic Prediction System with Live Map")

# ------------------ SIDEBAR ------------------
st.sidebar.header("🚗 Enter Trip Details")

start_area = st.sidebar.text_input("Start Area", "Delhi")
end_area = st.sidebar.text_input("End Area", "Noida")

distance = st.sidebar.number_input("Distance (km)", min_value=0.1, value=10.0)
avg_speed = st.sidebar.number_input("Average Speed (km/h)", min_value=1.0, value=40.0)

time_of_day = st.sidebar.slider("Time of Day (0–23)", 0, 23, 10)

day_of_week = st.sidebar.selectbox(
    "Day of Week",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)

# ❌ Removed manual weather input
traffic = st.sidebar.selectbox("Traffic Density", ["Low","Medium","High"])
road = st.sidebar.selectbox("Road Type", ["Highway","City","Rural"])

predict_btn = st.sidebar.button("🚀 Predict Travel Time")

# ------------------ GEOLOCATOR ------------------
geolocator = Nominatim(user_agent="traffic_app", timeout=10)

def get_coordinates(place):
    try:
        location = geolocator.geocode(place)
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
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

# ------------------ TRAFFIC COLOR FUNCTION ------------------
def get_traffic_color(level):
    if level == "Low":
        return "green"
    elif level == "Medium":
        return "orange"
    elif level == "High":
        return "red"
    return "blue"

# ------------------ MAP + LOGIC ------------------
if start_area and end_area:

    src_lat, src_lon = get_coordinates(start_area)
    dst_lat, dst_lon = get_coordinates(end_area)

    if src_lat and dst_lat:

        # Get real-time weather
        weather = get_weather(src_lat, src_lon)
        st.sidebar.write(f"🌦️ Live Weather: {weather}")

        # Center map
        mid_lat = (src_lat + dst_lat) / 2
        mid_lon = (src_lon + dst_lon) / 2

        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=11)

        # Start marker
        folium.Marker(
            [src_lat, src_lon],
            tooltip="Start",
            icon=folium.Icon(color="green")
        ).add_to(m)

        # Destination marker
        folium.Marker(
            [dst_lat, dst_lon],
            tooltip="Destination",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # Traffic-based route
        traffic_color = get_traffic_color(traffic)

        folium.PolyLine(
            [[src_lat, src_lon], [dst_lat, dst_lon]],
            color=traffic_color,
            weight=6,
            tooltip=f"Traffic: {traffic}"
        ).add_to(m)

        # Show map
        st.subheader("🗺️ Route Map")
        st_folium(m, width=900, height=500)

        # Traffic legend
        st.markdown("""
        ### 🚦 Traffic Legend
        - 🟢 Green → Low Traffic  
        - 🟠 Orange → Medium Traffic  
        - 🔴 Red → High Traffic  
        """)

        # ------------------ PREDICTION ------------------
        if predict_btn:

            data = {
                "start_area": start_area,
                "end_area": end_area,
                "distance_km": distance,
                "average_speed_kmph": avg_speed,
                "time_of_day": time_of_day,
                "day_of_week": day_of_week,
                "weather_condition": weather,  # auto weather
                "traffic_density_level": traffic,
                "road_type": road
            }

            try:
                response = requests.post(API_URL, json=data)

                if response.status_code == 200:
                    result = response.json()
                    st.success(
                        f"🚗 Estimated Travel Time: {result['travel_time']:.2f} minutes"
                    )
                else:
                    st.error("❌ API Error - Check backend")

            except Exception as e:
                st.error("❌ Cannot connect to API")

    else:
        st.warning("⚠️ Enter valid locations")

else:
    st.info("ℹ️ Please enter start and destination")
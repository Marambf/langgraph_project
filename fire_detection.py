from langchain.tools import tool
import requests
import pandas as pd
import folium
from datetime import datetime
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

@tool
def fire_detection_api_tool(city_name: str, target_date: str) -> str:
    """
    Detect fires around a city on a given date using NASA FIRMS real-time API.
    Returns summary and map.
    """
    try:
        # Get city coordinates
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.geocode(city_name)
        if location is None:
            return f"City '{city_name}' not found."
        latitude, longitude = location.latitude, location.longitude

        # NASA FIRMS API endpoint
        api_url = (
            "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            "MAP_KEY/VIIRS_SNPP_NRT/world/100"
        )  # replace MAP_KEY with your actual key

        # Request fire data
        response = requests.get(api_url)
        df = pd.read_csv(pd.compat.StringIO(response.text))

        # Parse and filter date
        df["acq_date"] = pd.to_datetime(df["acq_date"]).dt.date
        input_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        df_filtered = df[df["acq_date"] == input_date]

        # Distance filter
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            d_lat = radians(lat2 - lat1)
            d_lon = radians(lon2 - lon1)
            a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
            return R * 2 * atan2(sqrt(a), sqrt(1 - a))

        df_filtered["distance"] = df_filtered.apply(
            lambda row: haversine(latitude, longitude, row["latitude"], row["longitude"]),
            axis=1
        )
        df_filtered = df_filtered[df_filtered["distance"] <= 100]

        # Map
        fire_map = folium.Map(location=[latitude, longitude], zoom_start=6)
        for _, row in df_filtered.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color="red",
                fill=True,
                fill_opacity=0.6,
            ).add_to(fire_map)

        map_path = f"fire_map_{city_name}_{target_date}.html"
        fire_map.save(map_path)

        return f"{len(df_filtered)} fire events detected around {city_name} on {target_date}. Map saved at {map_path}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def fire_detection_csv_tool(csv_file_path: str, city_name: str, target_date: str) -> str:
    """
    Detect fires from NASA FIRMS CSV archive near a city and date.
    Returns summary and map.
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_file_path)

        required_columns = ["latitude", "longitude", "acq_date"]
        if not all(col in df.columns for col in required_columns):
            return "Missing required columns in the CSV."

        # City coords
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.geocode(city_name)
        if location is None:
            return f"City '{city_name}' not found."
        lat, lon = location.latitude, location.longitude

        df["acq_date"] = pd.to_datetime(df["acq_date"]).dt.date
        date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        df = df[df["acq_date"] == date_obj]

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            d_lat = radians(lat2 - lat1)
            d_lon = radians(lon2 - lon1)
            a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
            return R * 2 * atan2(sqrt(a), sqrt(1 - a))

        df["distance"] = df.apply(lambda row: haversine(lat, lon, row["latitude"], row["longitude"]), axis=1)
        df = df[df["distance"] <= 100]

        # Map
        fire_map = folium.Map(location=[lat, lon], zoom_start=6)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color="orange",
                fill=True,
                fill_opacity=0.6,
            ).add_to(fire_map)

        map_file = f"fire_csv_map_{city_name}_{target_date}.html"
        fire_map.save(map_file)

        return f"{len(df)} fire events found around {city_name} on {target_date} in archive. Map: {map_file}"

    except Exception as e:
        return f"Error: {str(e)}"
    

    
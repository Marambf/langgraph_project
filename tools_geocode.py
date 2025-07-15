#tools_geocode.py
import requests

def get_city_coordinates(city_name):
    url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        if not data:
            return None, None, city_name
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        display_name = data[0].get("display_name", city_name)
        name = display_name.split(",")[0]
        return lat, lon, name
    except Exception:
        return None, None, city_name

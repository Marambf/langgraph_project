import requests
from typing import Optional
from langchain.tools import tool

@tool
def weather_tool(city_name: str, forecast_days: Optional[int] = 5) -> str:
    """
    Récupère la météo actuelle et les prévisions pour une ville.
    :param city_name: Nom de la ville
    :param forecast_days: Nombre de jours de prévisions à afficher (par défaut 5)
    """
    # --- Géocodage via Nominatim ---
    geo_url = "https://nominatim.openstreetmap.org/search"
    geo_params = {"q": city_name, "format": "json", "limit": 1}
    geo_resp = requests.get(geo_url, params=geo_params, headers={"User-Agent": "weather-app"})
    geo_data = geo_resp.json()
    
    if not geo_data:
        return f"❌ Ville '{city_name}' introuvable."

    lat, lon = float(geo_data[0]["lat"]), float(geo_data[0]["lon"])

    # --- Appel API Open-Meteo ---
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "auto"
    }
    weather_resp = requests.get(weather_url, params=weather_params)
    if weather_resp.status_code != 200:
        return "❌ Impossible de récupérer la météo."

    weather_data = weather_resp.json()
    current = weather_data.get("current_weather", {})
    daily = weather_data.get("daily", {})

    # --- Formatage du résultat ---
    result = f"📍 Météo actuelle à {city_name} : {current.get('temperature')}°C, vent {current.get('windspeed')} km/h.\n"
    result += f"\nPrévisions pour les {forecast_days} prochains jours :\n"
    
    for date, tmax, tmin, rain in zip(
        daily.get("time", []),
        daily.get("temperature_2m_max", []),
        daily.get("temperature_2m_min", []),
        daily.get("precipitation_sum", [])
    ):
        result += f"{date} : Max {tmax}°C / Min {tmin}°C / Pluie {rain} mm\n"
        forecast_days -= 1
        if forecast_days == 0:
            break
    
    return result

#tools_weather.py
from langchain.tools import tool
import requests

@tool
def get_weather_data(city: str = "Tunis") -> str:
    """
    Récupère la météo actuelle pour une ville donnée via wttr.in (pas de clé API requise).
    - city: nom de la ville (ex: 'Tunis')
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        if response.status_code != 200:
            return f"❌ Erreur météo: {response.status_code} - {response.text}"
        data = response.json()
        current = data['current_condition'][0]
        desc = current['weatherDesc'][0]['value']
        temp = current['temp_C']
        return f"Météo à {city}: {desc}, {temp}°C"
    except Exception as e:
        return f"❌ Erreur lors de la récupération de la météo: {str(e)}"

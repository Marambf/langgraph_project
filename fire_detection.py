#fire_detection.py
from datetime import datetime, timedelta, date
import pandas as pd
import requests
import folium
import numpy as np
import os

MAP_KEY = 'f44596f0cc01c26985abd6bfff78ac92'
ARCHIVE_DIR = r"C:\Users\DELL\Documents\langgraph_project"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def get_city_coordinates(city_name):
    url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        if not data:
            return None, None
        return float(data[0]['lat']), float(data[0]['lon'])
    except:
        return None, None

def find_archive_file_for_date(date_obj):
    for filename in sorted(os.listdir(ARCHIVE_DIR)):
        if filename.endswith(".csv") and "fire_archive_" in filename:
            try:
                parts = filename.replace(".csv", "").split("_")
                start_year = int(parts[2])
                end_year = int(parts[3])
                start_date = datetime(start_year, 1, 21).date()
                end_date = datetime(end_year, 1, 20).date()
                if start_date <= date_obj <= end_date:
                    return os.path.join(ARCHIVE_DIR, filename)
            except:
                continue
    return None

def should_use_api(input_date_str):
    input_date = datetime.strptime(input_date_str, "%Y-%m-%d").date()
    return input_date >= (date.today() - timedelta(days=7))

def detect_fire_near_city(date_str, city_name, radius_km=100):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    lat_city, lon_city = get_city_coordinates(city_name)
    if lat_city is None:
        return None

    use_api = should_use_api(date_str)

    if use_api:
        url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_NOAA20_NRT/world/3'
        try:
            df = pd.read_csv(url)
        except:
            return None
    else:
        file_path = find_archive_file_for_date(date_obj)
        if not file_path:
            return None
        try:
            df = pd.read_csv(file_path)
        except:
            return None

    if "acq_date" not in df.columns or "latitude" not in df.columns or "longitude" not in df.columns:
        return None

    df = df[df["acq_date"] == date_str].copy()
    if df.empty:
        return None

    df["distance"] = df.apply(lambda row: haversine(lat_city, lon_city, row["latitude"], row["longitude"]), axis=1)
    df_filtered = df[df["distance"] <= radius_km]

    m = folium.Map(location=[lat_city, lon_city], zoom_start=7)
    for _, row in df_filtered.iterrows():
        popup = f"Brightness: {row.get('brightness', row.get('bright_ti4', 'N/A'))}, Date: {row['acq_date']}, Time: {row['acq_time']}"
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            popup=popup
        ).add_to(m)

    filename = f"incendies_{city_name.lower().replace(' ', '_')}_{date_str}.html"
    m.save(filename)
    return filename, len(df_filtered)

import re

def extract_params_from_text(text):
    """
    Extrait une date (YYYY-MM-DD), une ville, et un rayon depuis un texte libre.
    """
    date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
    date_str = date_match.group(1) if date_match else None

    rayon_match = re.search(r'(\d+)\s?km', text)
    rayon_km = int(rayon_match.group(1)) if rayon_match else 100  # défaut 100 km

    # 🔁 Amélioration : recherche du mot de type ville au début si pas de préposition détectée
    ville_match = re.search(r"(?:à|dans|autour de|près de|proche de|vers)\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\-']+)", text)
    
    if not ville_match:
        # Si pas de préposition, on tente de prendre le premier mot alphabétique avant la date
        if date_match:
            possible_ville = text[:date_match.start()].strip()
            if possible_ville:
                ville = possible_ville
            else:
                ville = None
        else:
            ville = None
    else:
        ville = ville_match.group(1).strip()

    return date_str, ville, rayon_km

from langchain.tools import tool

@tool
def detect_fire_tool(query_text: str) -> str:
    """
    Tool pour détecter des incendies à partir d'une requête en langage naturel.

    Cette fonction reçoit une phrase contenant une ville, une date au format YYYY-MM-DD,
    et éventuellement un rayon en kilomètres. Elle extrait ces informations,
    appelle la fonction principale de détection d'incendies autour de la ville à la date donnée,
    puis retourne un résumé clair du résultat.

    Exemple de requête acceptée :
        "Y a-t-il des incendies à Marseille le 2023-07-21 dans un rayon de 50 km ?"

    Paramètres :
    -----------
    query_text : str
        La requête utilisateur en langage naturel contenant ville, date et éventuellement rayon.

    Retour :
    --------
    str
        Un message résumant la détection des incendies : nombre, lieu, date,
        rayon, et fichier HTML généré avec la carte interactive.
        Retourne un message d'erreur si l'analyse échoue.
    """
    try:
        date_str, ville, rayon_km = extract_params_from_text(query_text)

        if not date_str or not ville:
            return "❌ Veuillez préciser une **ville** et une **date au format YYYY-MM-DD** dans votre requête."

        resultat = detect_fire_near_city(date_str, ville, rayon_km)
        if not resultat:
            return f"❌ Aucun incendie détecté ou problème lors du traitement de la requête pour **{ville}** le **{date_str}**."

        fichier, nb_incendies = resultat
        return f"✅ {nb_incendies} incendie(s) détecté(s) autour de {ville} le {date_str} dans un rayon de {rayon_km} km.\n🗺️ Carte : {fichier}"

    except Exception as e:
        return f"❌ Erreur inattendue lors du traitement : {str(e)}"


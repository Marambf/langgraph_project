# flood.py
import requests
import pycountry
import dateparser
from datetime import datetime
from typing import Optional
import folium
import re
from geopy.geocoders import Nominatim
import time
from langchain.tools import tool

# ✅ Tous les types de catastrophes pris en charge
VALID_DISASTER_TYPES = [
    "flood", "storm", "earthquake",
    "extreme temperature", "drought",
    "industrial accident", "transport"
]

def get_iso3_from_country_name(name):
    try:
        country = pycountry.countries.lookup(name)
        return country.alpha_3
    except LookupError:
        return None

def get_emdat_by_iso3(iso3_code):
    url = f"https://www.gdacs.org/gdacsapi/api/Emdat/getemdatbyiso3?iso3={iso3_code}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def filter_disasters_between_dates(events, start_date, end_date, disaster_type="flood"):
    filtered = []
    for event in events:
        # Gestion spéciale pour accidents industriels et transport
        if disaster_type == "industrial accident":
            if event.get("subgroupname", "").lower() != "industrial accident":
                continue
        elif disaster_type == "transport":
            if event.get("subgroupname", "").lower() != "transport":
                continue
        else:
            if event.get("disastertype", "").lower() != disaster_type:
                continue

        try:
            start_event = datetime(
                event.get("startyear", 0),
                event.get("startmonth", 0),
                event.get("startday", 0) or 1
            ).date()
            end_event = datetime(
                event.get("endyear", 0) or event.get("startyear", 0),
                event.get("endmonth", 0) or event.get("startmonth", 0),
                event.get("endday", 0) or event.get("startday", 0) or 1
            ).date()
        except Exception:
            continue

        if start_event <= end_date and end_event >= start_date:
            filtered.append(event)
    return filtered

def format_event_human_readable(event):
    start_date = f"{event.get('startday', '?')}/{event.get('startmonth', '?')}/{event.get('startyear', '?')}"
    end_date = f"{event.get('endday', '?')}/{event.get('endmonth', '?')}/{event.get('endyear', '?')}"

    disaster_emoji = {
        "flood": "🌊",
        "storm": "🌪️",
        "earthquake": "🏔️",
        "extreme temperature": "🥵",
        "drought": "🌵",
        "industrial accident": "🏭",
        "transport": "✈️"
    }.get(event.get("disastertype", "").lower(), "❗")

    return (
        f"{disaster_emoji} **{event.get('disastertype', event.get('subgroupname', '')).capitalize()} en {event.get('country', '?')} ({event.get('location', 'Lieu inconnu')})**\n"
        f"📍 Lieu : {event.get('location', 'Inconnu')}\n"
        f"📅 Du {start_date} au {end_date}\n"
        f"☠️ Décès : {event.get('totaldeaths', 'Non précisé')}\n"
        f"👥 Personnes affectées : {event.get('totalaffected', 'Non précisé')}\n"
        f"🧭 Origine : {event.get('origin', 'Non précisée')}\n"
        "--------------------------------------------------"
    )

def extract_dates_from_text(date_text: str) -> Optional[tuple[datetime.date, datetime.date]]:
    date_text = date_text.strip()
    dates = date_text.split()
    if len(dates) == 2:
        start_date = dateparser.parse(dates[0], languages=["fr", "en"])
        end_date = dateparser.parse(dates[1], languages=["fr", "en"])
        if start_date and end_date:
            return start_date.date(), end_date.date()

    interval_match = re.search(
        r"(du|from|entre)?\s*(.*?)\s*(au|to|et|et le)?\s*(.*)", 
        date_text, 
        re.IGNORECASE
    )
    if interval_match:
        start_raw = interval_match.group(2).strip()
        end_raw = interval_match.group(4).strip()
        start_date = dateparser.parse(start_raw, languages=["fr", "en"])
        end_date = dateparser.parse(end_raw, languages=["fr", "en"])
        if start_date and end_date:
            return start_date.date(), end_date.date()

    parsed = dateparser.parse(date_text, languages=["fr", "en"])
    if parsed:
        return parsed.date(), parsed.date()
    
    return None

def generate_disaster_map(events, disaster_type="flood", country="Unknown", start_date=None, map_filename=None):
    # Forcer toujours le nom du fichier à 'map.html'
    map_filename = "map.html"

    map_ = folium.Map(location=[45, 10], zoom_start=4)
    geolocator = Nominatim(user_agent="disaster_mapper")

    for event in events:
        location_name = event.get("location")
        country_name = event.get("country", "")
        lat = event.get("latitude")
        lon = event.get("longitude")

        start = f"{event.get('startday', '?')}/{event.get('startmonth', '?')}/{event.get('startyear', '?')}"
        end = f"{event.get('endday', '?')}/{event.get('endmonth', '?')}/{event.get('endyear', '?')}"
        popup_text = f"{location_name or 'Lieu inconnu'}, {country_name}<br>Du {start} au {end}"

        icon_color = {
            "flood": "blue",
            "storm": "darkred",
            "earthquake": "green",
            "extreme temperature": "orange",
            "drought": "beige",
            "industrial accident": "black",
            "transport": "purple"
        }.get(disaster_type, "gray")

        if lat and lon:
            try:
                folium.Marker(
                    location=[float(lat), float(lon)],
                    popup=popup_text,
                    icon=folium.Icon(color=icon_color, icon='info-sign')
                ).add_to(map_)
                continue
            except:
                pass

        if location_name:
            places = [p.strip() for p in re.split(',|;', location_name) if p.strip()]
            for place in places:
                try:
                    loc = geolocator.geocode(f"{place}, {country_name}", timeout=10)
                    if loc:
                        folium.Marker(
                            location=[loc.latitude, loc.longitude],
                            popup=popup_text,
                            icon=folium.Icon(color=icon_color, icon='info-sign')
                        ).add_to(map_)
                        time.sleep(1)
                        break
                except Exception as e:
                    print(f"Erreur géocodage pour {place}: {e}")
                    continue

    map_.save(map_filename)
    print(f"✅ Carte générée : {map_filename} (ouvrez-la dans un navigateur)")
    return map_filename


@tool
def query_disaster_events_tool(params: str) -> str:
    """
    Recherche des catastrophes naturelles et technologiques
    (inondation, tempête, tremblement de terre, température extrême, sécheresse,
    accident industriel, transport) dans un pays donné et pour une date ou plage de dates.
    
    params : texte libre comme "France 2015-06-29 temperature"
    """
    # -----------------------
    # Parse du texte libre
    # -----------------------
    words = params.split()
    if not words:
        return "❌ Entrée vide."

    country_name = words[0]  # premier mot = pays
    # Extraire la date (format ISO yyyy-mm-dd)
    date_expression = ' '.join([w for w in words[1:] if re.search(r'\d{4}-\d{2}-\d{2}', w)])
    # Le reste = type de catastrophe
    disaster_words = [w for w in words[1:] if not re.search(r'\d{4}-\d{2}-\d{2}', w)]
    disaster_type = ' '.join(disaster_words).lower() or 'flood'

    # Ajustements pour certains types
    if "temperature" in disaster_type:
        disaster_type = "extreme temperature"
    elif "accident" in disaster_type:
        disaster_type = "industrial accident"
    elif "transport" in disaster_type:
        disaster_type = "transport"

    # -----------------------
    # Code pays ISO3
    # -----------------------
    iso3 = get_iso3_from_country_name(country_name)
    if not iso3:
        return f"❌ Pays '{country_name}' non reconnu."

    # -----------------------
    # Extraction des dates
    # -----------------------
    dates = extract_dates_from_text(date_expression)
    if not dates:
        return f"❌ Impossible d'interpréter la date ou la plage de dates à partir de : '{date_expression}'"
    start_date, end_date = dates

    # -----------------------
    # Récupération des événements
    # -----------------------
    events = get_emdat_by_iso3(iso3)
    if not events:
        return f"❌ Aucune donnée trouvée pour le pays '{country_name}' (code {iso3})."

    filtered = filter_disasters_between_dates(events, start_date, end_date, disaster_type)
    if not filtered:
        return f"✅ Aucun événement '{disaster_type}' trouvé en {country_name} entre {start_date} et {end_date}."

    # -----------------------
    # Génération de la carte
    # -----------------------
    map_file = None
    if disaster_type != "transport":  # pas de carte pour transport
        map_file = generate_disaster_map(filtered, disaster_type, country_name, start_date)

    # -----------------------
    # Construction de la réponse
    # -----------------------
    result = f"✅ Événements '{disaster_type}' trouvés en {country_name} entre {start_date} et {end_date} :\n\n"
    for e in filtered:
        result += format_event_human_readable(e) + "\n"

    if map_file:
        result += f"\n🗺️ Une carte a été générée : {map_file}"

    return result

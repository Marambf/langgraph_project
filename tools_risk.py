# tools_risk.py
from datetime import date, datetime, timedelta
from tools_stac import query_stac_catalog
from langchain.tools import tool
import calendar
import re
from tools_geocode import get_city_coordinates 
from tools_weather import get_weather_data
import re
from datetime import datetime
from calendar import monthrange

mois_map = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
}

def extract_dates_from_text(text: str):
    text = text.lower()

    # 1. Intervalle complet : entre 5 mai 2023 et 12 juin 2023
    match = re.search(
        r"entre\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})\s+et\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})",
        text)
    if match:
        d1, m1, y1, d2, m2, y2 = match.groups()
        return f"{y1}-{mois_map[m1]:s}-{int(d1):02d}", f"{y2}-{mois_map[m2]:s}-{int(d2):02d}"

    # 2. Intervalle simple : entre 1 et 9 juin 2023
    match = re.search(
        r"entre\s+(\d{1,2})\s+et\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})",
        text)
    if match:
        d1, d2, m, y = match.groups()
        return f"{y}-{mois_map[m]:s}-{int(d1):02d}", f"{y}-{mois_map[m]:s}-{int(d2):02d}"

    # 3. Forme "du 01/06/2023 au 09/06/2023"
    match = re.search(r"du\s+(\d{2})/(\d{2})/(\d{4})\s+au\s+(\d{2})/(\d{2})/(\d{4})", text)
    if match:
        d1, m1, y1, d2, m2, y2 = match.groups()
        return f"{y1}-{m1}-{d1}", f"{y2}-{m2}-{d2}"

    # 4. Mois complet : "juin 2023"
    match = re.search(r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})", text)
    if match:
        m, y = match.groups()
        start = f"{y}-{mois_map[m]:s}-01"
        end_day = monthrange(int(y), int(mois_map[m]))[1]
        end = f"{y}-{mois_map[m]:s}-{end_day:02d}"
        return start, end

    # 5. Une seule date : "le 7 juillet 2023"
    match = re.search(r"le\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})", text)
    if match:
        d, m, y = match.groups()
        date = f"{y}-{mois_map[m]:s}-{int(d):02d}"
        return date, date

    return None, None  # si aucune date reconnue

@tool
def get_date() -> str:
    """Renvoie SEULEMENT la date sans commentaires"""
    return date.today().strftime("%d/%m/%Y")

@tool 
def get_time() -> str:
    """Renvoie SEULEMENT l'heure sans commentaires""" 
    return datetime.now().strftime("%Hh%M")

@tool
def calculator(expression: str) -> str:
    """Évalue une expression mathématique simple (ex: '23 * 7'). Format: 'nombre opérateur nombre'"""
    try:
        # Nettoyage de l'input
        cleaned = expression.strip().replace(' ', '')
        # Sécurité - seulement certains caractères autorisés
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in cleaned):
            return "Erreur: Caractères non autorisés dans l'expression"
        return str(eval(cleaned))
    except Exception:
        return "Erreur: Expression mathématique invalide"
    
@tool
def date_subtract(query: str) -> str:
    """
    Soustrait un nombre de jours à une date.
    Format attendu : 'AAAA-MM-JJ - jours'
    Exemple : '2025-12-31 - 38' -> '2025-11-23'
    """
    try:
        import re

        # Extraire la date et le nombre de jours avec une expression régulière
        match = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s*-\s*(\d+)\s*", query)
        if not match:
            return "❌ Format invalide. Utilise : 'AAAA-MM-JJ - jours'"

        date_str = match.group(1)
        days = int(match.group(2))

        base_date = datetime.strptime(date_str, "%Y-%m-%d")
        new_date = base_date - timedelta(days=days)

        return new_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"❌ Erreur : {str(e)}"
    


# tools_risk.py
# Corriger adjust_date pour accepter différents formats
@tool
def adjust_date(user_input: str) -> str:
    """
    Accepte une date au format 'YYYY-MM-DD' ou 'DD/MM/YYYY' et retourne la date de la veille (format 'YYYY-MM-DD').
    """
    try:
        if re.match(r"\d{2}/\d{2}/\d{4}", user_input):
            dt = datetime.strptime(user_input.strip(), "%d/%m/%Y")
        else:
            dt = datetime.strptime(user_input.strip(), "%Y-%m-%d")

        dt_prev = dt - timedelta(days=1)
        return dt_prev.strftime("%Y-%m-%d")
    except Exception as e:
        return f"❌ Erreur d'ajustement de date: {str(e)}"


@tool
def extract_bbox_and_dates(user_input: str) -> dict:
    """
    Extrait bbox, start_date, end_date, collection et ville depuis une phrase libre.
    Accepte formats comme : 'entre 1 et 9 juin 2023', 'du 01/06/2023 au 09/06/2023', etc.
    """
    try:
        if isinstance(user_input, dict):
            user_input = user_input.get("user_input", "")

        user_input = user_input.strip().lower()

        # --- Détection des dates via ta fonction générique ---
        start_date, end_date = extract_dates_from_text(user_input)
        if not start_date or not end_date:
            return {"error": "❌ Impossible de déterminer les dates."}

        # --- Détection de la collection ---
        collection_map = {
            "sentinel-1": "sentinel-1-grd",
            "sentinel 1": "sentinel-1-grd",
            "sentinel-2": "sentinel-2-l2a",
            "sentinel 2": "sentinel-2-l2a",
            "modis": "firms-modis-c6",
            "viirs": "firms-viirs-nrt"
        }

        collection = None
        for key, val in collection_map.items():
            if re.search(rf"\b{re.escape(key)}\b", user_input):
                collection = val
                break

        if not collection:
            return {"error": "❌ Collection non reconnue. Précise: sentinel-1, sentinel-2, modis, viirs."}

        # --- Détection de la ville ---
        city_match = re.search(r"de\s+([a-zA-Zéèàùçâêîôû\s\-]+?)(?=\s+(en|\d{4}|sentinel)|$)", user_input, re.IGNORECASE)
        if city_match:
            city = city_match.group(1).strip().title()
            lat, lon, _ = get_city_coordinates(city)
            if lat is None or lon is None:
                return {"error": f"❌ Ville '{city}' introuvable."}
            bbox = f"{lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}"
        else:
            return {"error": "❌ Impossible de détecter la ville dans la requête."}

        return {
            "bbox": bbox,
            "start_date": start_date,
            "end_date": end_date,
            "collection": collection,
            "city": city
        }

    except Exception as e:
        return {"error": f"❌ Erreur dans extract_bbox_and_dates: {str(e)}"}

   
    
from datetime import datetime, timedelta

def query_stac_with_retries(bbox_str, start_date_str, end_date_str, collection, query_func):
    """
    Effectue jusqu’à 3 tentatives de requête STAC en ajustant les dates si aucune image n’est trouvée.

    Stratégie d’ajustement des dates :
        - 1ère tentative : requête sur dates fournies
        - 2ème tentative : recule la date de fin d’un jour
        - 3ème tentative : recule la date de début d’un jour

    Arrête les tentatives dès qu’une image est trouvée, ou renvoie un message d’absence de données après 3 essais.

    Arguments :
        bbox_str : bbox sous forme "lon_min,lat_min,lon_max,lat_max"
        start_date_str : date début "YYYY-MM-DD"
        end_date_str : date fin "YYYY-MM-DD"
        collection : nom collection satellite
        query_func : fonction de requête STAC à appeler

    Retour :
        résultat de la requête ou message d’erreur/d’absence.
    """
    max_attempts = 3
    attempt = 0
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)

    while attempt < max_attempts:
        params = f"{bbox_str} {start_date.strftime(date_format)} {end_date.strftime(date_format)} {collection}"
        result = query_func(params)
        images = result.get("images", []) or result.get("features", [])  # Selon format de retour
        if images:
            return result
        if attempt == 0:
            # 1ère tentative: recule end_date d'un jour
            end_date -= timedelta(days=1)
        elif attempt == 1:
            # 2ème tentative: recule start_date d'un jour
            start_date -= timedelta(days=1)
        else:
            # Après 3 tentatives, abandonne
            return {
                "message": f"Aucune image trouvée pour {collection} entre {start_date.strftime(date_format)} et {end_date.strftime(date_format)} après plusieurs tentatives.",
                "collection": collection,
                "bbox": bbox_str,
                "start_date": start_date.strftime(date_format),
                "end_date": end_date.strftime(date_format),
                "images": []
            }
        attempt += 1



@tool
def query_stac_catalog_with_retry(params: str) -> dict:
    """
    Wrapper exposé en tant qu’outil LangChain qui encapsule la fonction query_stac_with_retries.

    Prend en entrée la chaîne params (format bbox start_date end_date collection), 
    découpe les paramètres et effectue plusieurs essais de requêtes STAC en cas d’échec.

    Retourne un dictionnaire de résultats ou un message d’erreur.
    """
    try:
        bbox_str, start_date, end_date, collection = params.split(" ")
        return query_stac_with_retries(bbox_str, start_date, end_date, collection, query_stac_catalog)
    except Exception as e:
        return {"error": f"❌ Erreur dans query_stac_catalog_with_retry: {str(e)}"}


def get_all_tools():
    return [
        get_date,
        get_time,
        calculator,
        extract_bbox_and_dates,
        query_stac_catalog,
        query_stac_catalog_with_retry,  # <-- ici on utilise la version avec retry
        adjust_date,
        get_weather_data,
        date_subtract
    ]
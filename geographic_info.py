import requests
from langchain.tools import tool

# --- Infos Pays ---
def get_country_info(country_name: str):
    """Retourne les informations principales d'un pays via l'API restcountries.com"""
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()[0]
    info = {
        "Type": "Pays",
        "Nom": data.get("name", {}).get("common"),
        "Capital": data.get("capital", ["Inconnue"])[0],
        "Population": data.get("population"),
        "Superficie (km²)": data.get("area"),
        "Région": data.get("region"),
        "Sous-région": data.get("subregion"),
        "Langues": list(data.get("languages", {}).values()),
        "Monnaie": ", ".join([v.get("name") for v in data.get("currencies", {}).values()]),
        "Drapeau": data.get("flags", {}).get("png")
    }
    return info

# --- Infos Ville (Nominatim + Wikidata) ---
def get_city_info(city_name: str):
    """Retourne les informations principales d'une ville via Nominatim + Wikidata (population)"""
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json&addressdetails=1&limit=1&extratags=1"
    headers = {"User-Agent": "GeoApp/1.0"}  # requis par Nominatim
    response = requests.get(url, headers=headers)
    if response.status_code != 200 or not response.json():
        return None
    data = response.json()[0]
    address = data.get("address", {})

    # population via Nominatim si dispo
    population = data.get("extratags", {}).get("population")

    # si pas trouvé → essayer Wikidata
    if not population:
        wikidata_id = data.get("extratags", {}).get("wikidata")
        if wikidata_id:
            wikidata_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
            r = requests.get(wikidata_url)
            if r.status_code == 200:
                wd = r.json()
                entity = wd.get("entities", {}).get(wikidata_id, {})
                claims = entity.get("claims", {})
                pop_claims = claims.get("P1082")  # P1082 = population
                if pop_claims:
                    population = pop_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("amount")
                    if population:
                        population = int(population.replace("+", ""))

    info = {
        "Type": "Ville",
        "Nom": data.get("display_name"),
        "Pays": address.get("country"),
        "Région": address.get("state"),
        "Latitude": data.get("lat"),
        "Longitude": data.get("lon"),
        "Population": population if population else "Inconnue"
    }
    return info


# --- TOOL LangChain ---
@tool
def geo_info_tool(name: str) -> str:
    """
    Retrieve geographic information about a country or a city.

    Parameters
    ----------
    name : str
        The name of the location (either a country or a city).
        Example: "France", "Tokyo", "Casablanca"

    Returns
    -------
    str
        A summary of the main information found (country or city).
    """
    # Essayer Pays
    info = get_country_info(name)

    # Si pas trouvé => Essayer Ville
    if not info:
        info = get_city_info(name)

    if not info:
        return f"Aucun résultat trouvé pour '{name}'."

    # Formater en texte lisible
    summary = "\n".join([f"{k} : {v}" for k, v in info.items()])
    return summary



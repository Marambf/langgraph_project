import requests
import folium
from langchain.tools import tool

# ---------- Géocodage via Nominatim (OSM) ----------
def geocode_place(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "route-steps-app"})
    r.raise_for_status()
    data = r.json()
    if not data:
        return None, None
    return float(data[0]["lat"]), float(data[0]["lon"])


# ---------- Itinéraire via OSRM (driving) ----------
def get_route(origin, destination):
    base = "http://router.project-osrm.org/route/v1/driving"
    url = f"{base}/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    params = {
        "overview": "false",
        "steps": "true",
        "alternatives": "false",
        "geometries": "geojson"
    }
    r = requests.get(url, params=params, headers={"User-Agent": "route-steps-app"})
    r.raise_for_status()
    return r.json()


# ---------- Helpers ----------
def human_distance(m):
    if m < 1000:
        return f"{int(round(m))} m"
    km = m / 1000.0
    return f"{km:.1f} km"

def human_duration(sec):
    minutes = int(round(sec / 60.0))
    if minutes < 60:
        return f"{minutes} min"
    h = minutes // 60
    m = minutes % 60
    return f"{h} h {m} min" if m else f"{h} h"

def modifier_fr(mod):
    return {
        "left": "à gauche",
        "right": "à droite",
        "slight left": "légèrement à gauche",
        "slight right": "légèrement à droite",
        "sharp left": "franchement à gauche",
        "sharp right": "franchement à droite",
        "straight": "tout droit",
        "uturn": "demi-tour",
        None: ""
    }.get(mod, mod if mod else "")

def road_label(step):
    name = (step.get("name") or "").strip()
    ref = (step.get("ref") or "").strip()
    if name and ref:
        return f"{ref} ({name})"
    return ref or name

def format_step(step):
    man = step.get("maneuver", {})
    stype = man.get("type")
    mod = man.get("modifier")
    exit_no = man.get("exit")
    road = road_label(step)
    dist = human_distance(step.get("distance", 0))

    dir_txt = modifier_fr(mod)
    on_road = f" sur {road}" if road else ""

    if stype == "depart":
        return f"Départ{on_road}."
    if stype == "arrive":
        return "Vous êtes arrivé."
    if stype == "turn":
        return f"Tournez {dir_txt}{on_road} ({dist})." if dir_txt else f"Tournez{on_road} ({dist})."
    if stype == "continue":
        if dir_txt and dir_txt != "tout droit":
            return f"Continuez {dir_txt}{on_road} ({dist})."
        return f"Continuez{on_road} ({dist})."
    if stype == "new name":
        return f"Continuez, la route devient{on_road} ({dist})."
    if stype == "end of road":
        return f"Au bout de la route, tournez {dir_txt}{on_road} ({dist})." if dir_txt else f"Au bout de la route, continuez{on_road} ({dist})."
    if stype in ("merge",):
        return f"Rejoignez{on_road} ({dist})."
    if stype in ("on ramp", "ramp"):
        return f"Prenez la bretelle {dir_txt}{on_road} ({dist})." if dir_txt else f"Prenez la bretelle{on_road} ({dist})."
    if stype in ("off ramp",):
        return f"Prenez la sortie {dir_txt}{on_road} ({dist})." if dir_txt else f"Prenez la sortie{on_road} ({dist})."
    if stype in ("fork",):
        return f"À la bifurcation, prenez {dir_txt}{on_road} ({dist})." if dir_txt else f"À la bifurcation, suivez{on_road} ({dist})."
    if stype in ("roundabout", "rotary"):
        return f"Au rond-point, prenez la sortie {exit_no}{on_road} ({dist})." if exit_no else f"Au rond-point, continuez{on_road} ({dist})."
    if stype == "uturn":
        return f"Faites demi-tour{on_road} ({dist})."

    if dir_txt and road:
        return f"{stype.capitalize()} {dir_txt} sur {road} ({dist})."
    if road:
        return f"{stype.capitalize()} sur {road} ({dist})."
    return f"{stype.capitalize()} ({dist})."


# ---------- Génération de carte ----------
def create_map(lat1, lon1, lat2, lon2, route_data, start, end):
    m = folium.Map(location=[lat1, lon1], zoom_start=12)
    for leg in route_data.get("routes", []):
        for l in leg.get("legs", []):
            coords = []
            for step in l.get("steps", []):
                geom = step.get("geometry", {}).get("coordinates", [])
                coords.extend([(lat, lon) for lon, lat in geom])
            if coords:
                folium.PolyLine(coords, color="blue", weight=5, opacity=0.8).add_to(m)

    folium.Marker([lat1, lon1], tooltip=f"Départ: {start}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([lat2, lon2], tooltip=f"Arrivée: {end}", icon=folium.Icon(color="red")).add_to(m)

    file_name = "itineraire.html"
    m.save(file_name)
    return file_name


# ---------- Tool intégré ----------
@tool("get_route_info", return_direct=True)
def get_route_info(query: str) -> str:
    """
    Calcule un itinéraire en voiture entre deux lieux.
    Input format: "Start -> End"
    Example: "Paris -> Lyon"
    Output: Résumé de l'itinéraire avec distance, durée et étapes.
    Une carte interactive est également enregistrée en HTML.
    """
    if "->" not in query:
        return "Format attendu: 'Lieu de départ -> Destination'."

    start, end = [x.strip() for x in query.split("->")]

    lat1, lon1 = geocode_place(start)
    lat2, lon2 = geocode_place(end)
    if not lat1 or not lon1 or not lat2 or not lon2:
        return "❌ Lieu introuvable."

    try:
        data = get_route((lat1, lon1), (lat2, lon2))
    except requests.RequestException as e:
        return f"❌ Erreur réseau : {e}"

    if not data or data.get("code") != "Ok" or not data.get("routes"):
        return "❌ Impossible de calculer l'itinéraire."

    route = data["routes"][0]
    total_dist = human_distance(route["distance"])
    total_dur = human_duration(route["duration"])

    steps_txt = []
    step_index = 1
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            steps_txt.append(f"{step_index}. {format_step(step)}")
            step_index += 1

    file_name = create_map(lat1, lon1, lat2, lon2, data, start, end)

    return (
        f"🚗 Itinéraire de {start} à {end}\n"
        f"Distance totale : {total_dist}\n"
        f"Durée estimée   : {total_dur}\n\n"
        + "\n".join(steps_txt)
        + f"\n\n🗺️ Carte enregistrée dans le fichier : {file_name}"
    )
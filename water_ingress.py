import os
import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import folium
from langchain.tools import tool

# ---------- Clé API OpenTopography ----------
OPENTOP_API_KEY = os.getenv("OPENTOPO_API_KEY", "811d1f7cbb4522dc7e623ec70a657ed1")

# ---------- Géocodage direct (nom → lat/lon) ----------
def geocode_city(city_name: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "SurfaceIngressTool"})
    data = r.json()
    if not data:
        raise ValueError(f"Ville non trouvée: {city_name}")
    return float(data[0]["lat"]), float(data[0]["lon"])

# ---------- Géocodage inversé (lat/lon → ville/pays) ----------
def reverse_geocode(lat: float, lon: float):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "addressdetails": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "SurfaceIngressTool"})
    data = r.json()
    address = data.get("address", {})
    city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
    country = address.get("country")
    country_code = address.get("country_code")
    return {"city": city, "country": country, "country_iso": country_code.upper() if country_code else None}

# ---------- Télécharger DEM ----------
def download_dem_opentopo(lat: float, lon: float, buffer_deg=0.01, dem_file="dem_city.tif"):
    min_lat, max_lat = lat - buffer_deg, lat + buffer_deg
    min_lon, max_lon = lon - buffer_deg, lon + buffer_deg
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": "SRTMGL3",
        "west": min_lon, "south": min_lat, "east": max_lon, "north": max_lat,
        "outputFormat": "GTiff", "API_Key": OPENTOP_API_KEY
    }
    r = requests.get(url, params=params, stream=True)
    if r.status_code != 200:
        raise ValueError(f"Impossible de télécharger le DEM. Statut: {r.status_code}")
    with open(dem_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dem_file

# ---------- D8 Flow Direction & Accumulation ----------
def d8_flow_direction_and_accum(dem: np.ndarray):
    neighbors = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    h, w = dem.shape
    dir_idx = np.full((h, w), -1, dtype=int)
    for y in range(1, h-1):
        for x in range(1, w-1):
            z0 = dem[y, x]
            zmin = z0
            kmin = -1
            for k, (dy, dx) in enumerate(neighbors):
                z = dem[y + dy, x + dx]
                if z < zmin:
                    zmin = z
                    kmin = k
            dir_idx[y, x] = kmin
    acc = np.ones_like(dem, dtype=np.float32)
    indices = np.argsort(dem, axis=None)
    ys, xs = np.unravel_index(indices, dem.shape)
    for y, x in zip(ys, xs):
        k = dir_idx[y, x]
        if k >= 0:
            dy, dx = neighbors[k]
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w:
                acc[yy, xx] += acc[y, x]
    return acc, dir_idx

# ---------- Actions d'atténuation ----------
def mitigation_rules(dem, slope, acc, risk_mask):
    actions = []
    risk_percent = 100.0 * np.sum(risk_mask) / risk_mask.size
    mean_slope_rel = np.nanmean(slope)
    high_acc_mask = acc >= np.percentile(acc, 95)
    low_mask = dem <= np.percentile(dem, 5)

    if risk_percent >= 10:
        actions += [{"description": "Créer des rigoles ou bermes pour détourner l’eau en amont.",
                     "resource": "https://www.ecologie.gouv.fr/sites/default/files/documents/Gestion_durable_des_eaux_pluviales_le_plan_daction.pdf"},
                    {"description": "Installer des flood boards ou sacs de sable aux ouvertures.",
                     "resource": "https://www.georisques.gouv.fr/reduire-la-vulnerabilite-de-ma-maison-aux-inondations"}]

    if mean_slope_rel < 0.02:
        actions += [{"description": "Reprofiler le terrain pour une pente > 2%.",
                     "resource": "https://www.cerema.fr/fr/actualites/gestion-durable-eaux-pluviales-etude-benefices-apportes"},
                    {"description": "Ajouter un caniveau linéaire devant les seuils raccordé au réseau pluvial.",
                     "resource": "https://www.sdea.fr/images/SDEA/GEPU/Guide_pratique_particulier_WEB.pdf"}]

    if np.any(high_acc_mask & risk_mask):
        actions += [{"description": "Installer un drain français le long des lignes d’écoulement.",
                     "resource": "https://www.sdea.fr/images/SDEA/GEPU/Guide_pratique_particulier_WEB.pdf"},
                    {"description": "Entretenir les caniveaux/avaloirs et vérifier les exutoires.",
                     "resource": "https://www.cerema.fr/fr/actualites/gestion-durable-eaux-pluviales-etude-benefices-apportes"}]

    if np.any(low_mask & risk_mask):
        actions += [{"description": "Créer un point bas contrôlé avec pompe.",
                     "resource": "https://www.biodiversite-centrevaldeloire.fr/comprendre/les-solutions-d-adaptation-fondees-sur-la-nature/des-solutions-pour-reduire-les-risques-inondations"},
                    {"description": "Remblayer légèrement les cuvettes proches des façades.",
                     "resource": "https://www.adaptation-changement-climatique.gouv.fr/dossiers-thematiques/impacts/inondation"}]

    if 3 <= risk_percent < 10 and mean_slope_rel >= 0.02:
        actions += [{"description": "Planter des bandes végétalisées (bioswales).",
                     "resource": "https://www.ecologie.gouv.fr/sites/default/files/documents/Gestion_durable_des_eaux_pluviales_le_plan_daction.pdf"},
                    {"description": "Diriger les descentes de gouttières loin des fondations.",
                     "resource": "https://www.georisques.gouv.fr/reduire-la-vulnerabilite-de-ma-maison-aux-inondations"}]

    actions += [{"description": "Nettoyer régulièrement les grilles, caniveaux et regards.",
                 "resource": "https://www.environnement.gouv.qc.ca/eau/pluviales/guide-gestion-eaux-pluviales.pdf"},
                {"description": "Vérifier l’étanchéité des seuils et joints.",
                 "resource": "https://www.ecologie.gouv.fr/politiques-publiques/prevention-inondations"}]

    # Supprimer doublons
    seen = set()
    unique_actions = []
    for a in actions:
        if a["description"] not in seen:
            unique_actions.append(a)
            seen.add(a["description"])
    return unique_actions

# ---------- Estimation principale ----------
def estimate_surface_water_ingress(location_input):
    if isinstance(location_input, str):
        lat, lon = geocode_city(location_input)
    elif isinstance(location_input, (tuple, list)) and len(location_input) == 2:
        lat, lon = location_input
    else:
        raise ValueError("Input invalide. Utiliser un nom de ville ou un tuple (lat, lon).")
    location_info = reverse_geocode(lat, lon)

    dem_file = download_dem_opentopo(lat, lon, buffer_deg=0.01)
    try:
        with rasterio.open(dem_file) as src:
            dem = src.read(1).astype(np.float32)
            if src.nodata is not None:
                dem[dem == src.nodata] = np.nan
            dem[np.isnan(dem)] = np.nanmedian(dem)
            transform = src.transform

        gy, gx = np.gradient(dem)
        slope = np.sqrt(gx**2 + gy**2)
        acc, _ = d8_flow_direction_and_accum(dem)

        low_mask = dem <= np.nanpercentile(dem, 15)
        flat_mask = slope <= 0.02
        highacc = acc >= np.percentile(acc, 90)
        risk_mask = (low_mask & flat_mask) | highacc

        stats = {
            "DEM_shape": dem.shape,
            "Elevation_min": float(np.nanmin(dem)),
            "Elevation_max": float(np.nanmax(dem)),
            "Elevation_mean": float(np.nanmean(dem)),
            "Slope_mean": float(np.nanmean(slope)),
            "Risk_zone_percent": float(100.0 * np.sum(risk_mask) / risk_mask.size)
        }

        actions = mitigation_rules(dem, slope, acc, risk_mask)

        # Cartes Matplotlib
        plt.imsave("map_elevation.png", dem, cmap="terrain")
        plt.imsave("map_slope.png", slope, cmap="inferno")
        plt.imsave("map_flowacc.png", acc, cmap="Blues")
        plt.imsave("map_risk.png", risk_mask.astype(float), cmap="Reds")

        # Carte Folium
        risk_coords = np.argwhere(risk_mask)
        folium_map = folium.Map(location=[lat, lon], zoom_start=14)
        for y, x in risk_coords:
            try:
                rlon, rlat = rasterio.transform.xy(transform, y, x)
                folium.CircleMarker(location=[rlat, rlon], radius=2, color='red', fill=True, fill_opacity=0.7).add_to(folium_map)
            except Exception:
                continue
        folium_map.save("map_risk_folium.html")

        return {
            "Ingress_paths_estimate": "L’eau suit les lignes d’écoulement (D8) vers les points bas.",
            "Mitigation_actions": actions,
            **stats,
            "Maps": {
                "Elevation": "map_elevation.png",
                "Slope": "map_slope.png",
                "FlowAccumulation": "map_flowacc.png",
                "Risk": "map_risk.png",
                "Risk_Folium": "map_risk_folium.html"
            },
            "Explanation": (
                "📊 Comment lire les cartes :\n"
                "1. Carte d’altitude : relief (zones sombres = basses).\n"
                "2. Carte de pente : pentes fortes = écoulement rapide.\n"
                "3. Carte de flux : chemins probables de l’eau.\n"
                "4. Carte de risque : zones rouges = accumulation probable."
            ),
            "Location": location_info
        }
    finally:
        if os.path.exists(dem_file):
            os.remove(dem_file)
# ---------- Tool LangChain ----------
@tool
def estimate_surface_water_ingress_tool(location_input: str) -> dict:
    """
    Analyse complète du risque d’infiltration d’eau de surface pour une zone donnée.

    Cette fonction prend en entrée soit :
    - un nom de ville (str), par exemple "Paris",
    - ou un tuple de coordonnées (latitude, longitude), par exemple (48.8566, 2.3522).

    Elle retourne un dictionnaire contenant :

    1. Ingress_paths_estimate : Description textuelle de la trajectoire probable de l’eau (D8 flow).
    2. Mitigation_actions : Liste d’actions recommandées pour réduire le risque d’infiltration.
    3. Statistics : Statistiques sur le DEM (Digital Elevation Model) et les zones à risque :
       - DEM_shape : dimensions du DEM
       - Elevation_min / Elevation_max / Elevation_mean : altitudes
       - Slope_mean : pente moyenne
       - Risk_zone_percent : pourcentage de zone à risque
    4. Maps : Chemins vers les cartes générées :
       - Elevation, Slope, FlowAccumulation, Risk (Matplotlib)
       - Risk_Folium (carte interactive Folium)
    5. Explanation : Explications pour lire les cartes.
    6. error : Message d’erreur si le calcul échoue.

    Processus effectué :
    - Géocodage (nom de ville -> lat/lon) si nécessaire.
    - Téléchargement du DEM via OpenTopography.
    - Calcul de la pente et de l’accumulation de flux D8.
    - Identification des zones à risque selon faible élévation, faible pente, accumulation élevée.
    - Génération des cartes Matplotlib et Folium.
    - Application de règles de mitigation pour proposer des actions correctives.
    """
    try:
        result = estimate_surface_water_ingress(location_input)
        return {
            "Ingress_paths_estimate": result.get("Ingress_paths_estimate", "Non disponible"),
            "Mitigation_actions": result.get("Mitigation_actions", []),
            "Statistics": {
                "DEM_shape": result.get("DEM_shape"),
                "Elevation_min": result.get("Elevation_min"),
                "Elevation_max": result.get("Elevation_max"),
                "Elevation_mean": result.get("Elevation_mean"),
                "Slope_mean": result.get("Slope_mean"),
                "Risk_zone_percent": result.get("Risk_zone_percent")
            },
            "Maps": result.get("Maps", {}),
            "Explanation": result.get("Explanation", "Non disponible"),
            "error": result.get("error")
        }
    except Exception as e:
        return {
            "error": str(e),
            "Ingress_paths_estimate": "Non disponible",
            "Mitigation_actions": [],
            "Statistics": {},
            "Maps": {},
            "Explanation": "Non disponible"
        }

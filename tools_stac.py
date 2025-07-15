from langchain_core.tools import tool
import requests
from datetime import datetime, timedelta


STAC_API_URL = "https://earth-search.aws.element84.com/v1"

from datetime import datetime, timedelta

@tool
def query_stac_catalog(params: str) -> dict:
    """
    Interroge le catalogue STAC EarthSearch pour récupérer des images satellites correspondant à une 
    zone géographique (bbox), une période et une collection données.

    Le paramètre `params` doit être une chaîne de caractères contenant :
        - bbox au format "lon_min,lat_min,lon_max,lat_max"
        - date de début au format "YYYY-MM-DD"
        - date de fin au format "YYYY-MM-DD"
        - nom de la collection (ex: sentinel-1-grd, sentinel-2-l2a)

    Exemple de `params` : "10.1,36.7,10.3,36.9 2023-07-01 2023-07-10 sentinel-1-grd"

    Fonctionnement :
    - Découpe la période en jours et effectue une requête POST pour chaque jour.
    - Récupère une image par jour avec ses métadonnées (date, taux de couverture nuageuse, vignette).
    - Construit une liste des images trouvées sur la période.

    Retour :
    - Un dictionnaire avec :
        * collection, bbox, start_date, end_date,
        * liste des images (date, cloud_cover, thumbnail)
    - En cas d’absence d’image, un message explicite.
    - En cas d’erreur, un dictionnaire avec la clé "error".

    Exceptions gérées pour retourner une erreur lisible.
    """
    try:
        bbox_str, start_date, end_date, collection = params.split(" ")
        bbox = [float(x) for x in bbox_str.split(",")]
        date_format = "%Y-%m-%d"
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)

        all_images = []

        current = start
        while current <= end:
            date_str = current.strftime(date_format)
            url = (
                f"https://earth-search.aws.element84.com/v1/search"
            )
            body = {
                "collections": [collection],
                "bbox": bbox,
                "datetime": f"{date_str}T00:00:00Z/{date_str}T23:59:59Z",
                "limit": 1
            }

            response = requests.post(url, json=body)
            if response.status_code == 200:
                items = response.json().get("features", [])
                if items:
                    item = items[0]
                    image_data = {
                        "date": date_str,
                        "cloud_cover": item["properties"].get("eo:cloud_cover", "N/A"),
                        "thumbnail": item["assets"].get("thumbnail", {}).get("href", "No thumbnail")
                    }
                    all_images.append(image_data)
            current += timedelta(days=1)

        if not all_images:
            return {
                "message": f"📭 Aucune image trouvée pour {collection} entre {start_date} et {end_date}.",
                "collection": collection,
                "bbox": bbox_str,
                "start_date": start_date,
                "end_date": end_date,
                "images": []
            }
        
        return {
    "collection": collection,
    "bbox": bbox_str,
    "start_date": start_date,
    "end_date": end_date,
    "images": all_images,
    "urls": [img["thumbnail"] for img in all_images if "thumbnail" in img]
}

    
    except Exception as e:
        return {"error": f"❌ Erreur lors de la requête STAC: {str(e)}"}
    
    
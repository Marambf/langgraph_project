# tools_stac.py
from langchain_core.tools import tool
import requests
from datetime import datetime, timedelta
import re

STAC_API_URL = "https://earth-search.aws.element84.com/v1"

@tool
def query_stac_catalog(params: str) -> dict:
    """
    Interroge le catalogue STAC EarthSearch pour récupérer des images satellites correspondant à une 
    zone géographique (bbox), une période et une collection données.

    Format de `params` : "lon_min,lat_min,lon_max,lat_max start_date end_date collection"
    Exemple : "10.1,36.7,10.3,36.9 2023-07-01 2023-07-10 sentinel-2-l2a"
    """
    try:
        # Regex robuste pour séparer les 4 parties du paramètre
        match = re.match(r"([\d\.\,\-]+)\s+(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+([\w\-]+)", params.strip())
        if not match:
            return {"error": f"❌ Format invalide pour les paramètres STAC : {params}"}

        bbox_str, start_date, end_date, collection = match.groups()
        bbox = [float(x) for x in bbox_str.split(",")]
        date_format = "%Y-%m-%d"
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)

        all_images = []
        current = start

        while current <= end:
            date_str = current.strftime(date_format)
            body = {
                "collections": [collection],
                "bbox": bbox,
                "datetime": f"{date_str}T00:00:00Z/{date_str}T23:59:59Z",
                "limit": 1
            }

            response = requests.post(f"{STAC_API_URL}/search", json=body)
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

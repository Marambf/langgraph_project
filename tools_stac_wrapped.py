# tools_stac_wrapped.py

from langchain.tools import tool
from tools_parsing import extract_bbox_and_dates, query_stac_catalog_with_retry


@tool
def get_satellite_images(user_query: str) -> dict:
    """
    Analyse automatiquement la requête pour en extraire bbox, dates et collection,
    puis interroge le catalogue STAC pour récupérer des images satellites.

    Cette fonction combine extract_bbox_and_dates et query_stac_catalog_with_retry.
    """
    parsed = extract_bbox_and_dates(user_query)
    if "error" in parsed:
        return {"error": parsed["error"]}
    
    bbox = parsed["bbox"]
    start_date = parsed["start_date"]
    end_date = parsed["end_date"]
    collection = parsed["collection"]
    
    params = f"{bbox} {start_date} {end_date} {collection}"
    return query_stac_catalog_with_retry(params)

from __future__ import annotations
from typing import Any, Dict
from sat_ingest.core.models import Item, Asset

def map_coda_item(raw: Dict[str, Any]) -> Item:
    """
    Map a CODA API STAC-like Feature into our internal Item model.
    Adds RGB aliases for quicklook.
    Also maps Sentinel-3 OLCI band names to red/green/blue if present.
    """

    props = raw.get("properties", {})
    assets_raw = raw.get("assets", {})

    # Build Asset objects
    assets: Dict[str, Asset] = {}
    for key, a in assets_raw.items():
        assets[key] = Asset(
            href=a.get("href"),
            type=a.get("type"),
            title=a.get("title"),
            roles=a.get("roles"),
        )

    # Alias Sentinel-style B04/B03/B02
    if "B04" in assets:
        assets["red"] = assets["B04"]
    if "B03" in assets:
        assets["green"] = assets["B03"]
    if "B02" in assets:
        assets["blue"] = assets["B02"]

    # Alias Sentinel-3 OLCI bands to RGB equivalents
    # Typical: Oa08 ~ red, Oa06 ~ green, Oa04 ~ blue
    if "Oa08" in assets and "red" not in assets:
        assets["red"] = assets["Oa08"]
    if "Oa06" in assets and "green" not in assets:
        assets["green"] = assets["Oa06"]
    if "Oa04" in assets and "blue" not in assets:
        assets["blue"] = assets["Oa04"]

    return Item(
        id=raw.get("id"),
        collection=raw.get("collection", props.get("collection")),
        datetime=props.get("datetime") or props.get("startDate"),
        geometry=raw.get("geometry"),
        bbox=raw.get("bbox"),
        properties=props,
        assets=assets,
        links=raw.get("links", []),
    )

from __future__ import annotations
from sat_ingest.core.models import Item, Asset

# Very small mapping from a STAC Item dict to Item dataclass.

def map_stac_item(d: dict) -> Item:
    assets = {k: Asset(key=k, href=v.get("href"), media_type=v.get("type"), roles=tuple(v.get("roles", [])))
              for k, v in d.get("assets", {}).items()}
    return Item(
        id=d.get("id"),
        collection=d.get("collection"),
        datetime=d.get("properties", {}).get("datetime"),
        bbox=d.get("bbox"),
        geometry=d.get("geometry"),
        properties=d.get("properties", {}),
        assets=assets,
    )


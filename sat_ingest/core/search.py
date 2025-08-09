

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re

def _normalize_datetime(dt: str) -> str:
    """
    Accepts:
      - 'YYYY-MM-DD/YYYY-MM-DD'
      - 'YYYY-MM-DD' (single day)
    Returns RFC3339 range:
      'YYYY-MM-DDT00:00:00Z/YYYY-MM-DDT23:59:59Z'
    Leaves other inputs unchanged.
    """
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}", dt):
        start, end = dt.split("/")
        return f"{start}T00:00:00Z/{end}T23:59:59Z"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt):
        return f"{dt}T00:00:00Z/{dt}T23:59:59Z"
    return dt

@dataclass
class SearchParams:
    collections: Optional[list[str]] = None
    time: Optional[str] = None  # ISO-8601 range or full RFC3339
    intersects: Optional[dict] = None  # GeoJSON geometry
    bbox: Optional[list[float]] = None  # [minx, miny, maxx, maxy]
    limit: int = 100
    query: Optional[dict] = None  # provider-specific filters

    def to_stac_payload(self) -> dict:
        body = {
            "collections": self.collections,
            "datetime": _normalize_datetime(self.time) if self.time else None,
            "intersects": self.intersects,
            "bbox": self.bbox,
            "limit": self.limit,
            "query": self.query,
        }
        return {k: v for k, v in body.items() if v is not None}



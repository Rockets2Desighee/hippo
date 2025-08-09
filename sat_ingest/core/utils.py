# sat_ingest/core/utils.py
import json
from pathlib import Path
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj

def load_aoi(path: str) -> dict:
    """Load shapefile/KML/GeoJSON into a GeoJSON geometry in WGS84."""
    from fiona import open as fopen  # lazy import to avoid heavy deps unless needed
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".geojson", ".json"):
        return json.loads(p.read_text())
    elif ext in (".shp", ".kml"):
        with fopen(p) as src:
            geom = shape(next(iter(src))["geometry"])
            if src.crs and src.crs.to_string() != "EPSG:4326":
                proj = pyproj.Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True).transform
                geom = transform(proj, geom)
            return mapping(geom)
    else:
        raise ValueError(f"Unsupported AOI format: {ext}")




# # sat_ingest/core/geometry.py
# from __future__ import annotations
# import json
# import pathlib
# from shapely.geometry import shape, mapping
# from shapely.ops import transform
# import pyproj

# def load_aoi(path: str) -> dict:
#     """
#     Load a GeoJSON, Shapefile, or WKT file and return a GeoJSON geometry dict.
#     - Reprojects to EPSG:4326 if needed.
#     - Supports .geojson, .json, .shp, .wkt
#     """
#     p = pathlib.Path(path)
#     ext = p.suffix.lower()

#     if ext in (".geojson", ".json"):
#         with open(p) as f:
#             gj = json.load(f)
#         geom = shape(gj.get("geometry", gj))
#     elif ext == ".wkt":
#         from shapely import wkt
#         with open(p) as f:
#             geom = wkt.loads(f.read())
#     elif ext == ".shp":
#         import fiona
#         with fiona.open(p) as src:
#             first = next(iter(src))
#             geom = shape(first["geometry"])
#             src_crs = src.crs
#             if src_crs and src_crs.to_string() != "EPSG:4326":
#                 transformer = pyproj.Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
#                 geom = transform(transformer.transform, geom)
#     else:
#         raise ValueError(f"Unsupported AOI file format: {ext}")

#     return mapping(geom)







from pathlib import Path
from typing import Tuple, Union
from shapely.geometry import shape, mapping
import fiona
from rasterio.crs import CRS

def load_aoi_geometry(aoi_path: Union[str, Path]) -> Tuple[dict, CRS]:
    """
    Load an AOI file and return (geometry_geojson, CRS).
    - Always returns a JSON-serializable GeoJSON dict.
    - Always returns a valid rasterio.CRS (defaults to EPSG:4326 if missing).
    """
    aoi_path = Path(aoi_path)

    # Case 1: Vector formats (Shapefile, GeoJSON, etc.)
    try:
        with fiona.open(aoi_path) as src:
            crs = CRS.from_user_input(src.crs) if src.crs else CRS.from_epsg(4326)
            geom = shape(next(iter(src))["geometry"])
            return mapping(geom), crs
    except Exception:
        pass

    # Case 2: WKT in a text file
    try:
        from shapely import wkt
        text = aoi_path.read_text().strip()
        geom = wkt.loads(text)
        return mapping(geom), CRS.from_epsg(4326)
    except Exception:
        pass

    raise RuntimeError(f"Unsupported AOI format or failed to load: {aoi_path}")


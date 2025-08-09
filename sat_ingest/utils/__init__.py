import pathlib
import json
import fiona
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj


def load_aoi_geometry(aoi_path: str):
    """
    Load an AOI geometry from .geojson, .json, .shp, or .kml.
    Returns a (bbox, geojson_dict) tuple.
    """
    p = pathlib.Path(aoi_path)
    suffix = p.suffix.lower()

    if suffix in (".geojson", ".json"):
        with open(p, "r") as f:
            data = json.load(f)
        geom = shape(data if "type" in data and "coordinates" in data else data["features"][0]["geometry"])
    elif suffix in (".shp", ".kml"):
        with fiona.open(p) as src:
            first = next(iter(src))
            geom = shape(first["geometry"])
    else:
        raise ValueError(f"Unsupported AOI format: {suffix}")

    # Reproject to EPSG:4326 if needed
    if hasattr(geom, "crs") and geom.crs and geom.crs.to_epsg() != 4326:
        project = pyproj.Transformer.from_crs(geom.crs, "EPSG:4326", always_xy=True).transform
        geom = transform(project, geom)

    return geom.bounds, mapping(geom)


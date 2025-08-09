from pathlib import Path
from typing import Tuple, Union
from shapely.geometry import shape, Polygon, MultiPolygon
import fiona
from rasterio.crs import CRS

def load_aoi_geometry(aoi_path: Union[str, Path]) -> Tuple[Union[Polygon, MultiPolygon], CRS]:
    """
    Load AOI from file and return (geometry, CRS).
    Defaults to EPSG:4326 if CRS missing.
    """
    aoi_path = Path(aoi_path)

    # Vector formats readable by Fiona
    try:
        with fiona.open(aoi_path) as src:
            crs = CRS.from_user_input(src.crs) if src.crs else CRS.from_epsg(4326)
            geom = shape(next(iter(src))["geometry"])
            return geom, crs
    except Exception:
        pass

    # WKT fallback
    try:
        from shapely import wkt
        text = aoi_path.read_text().strip()
        geom = wkt.loads(text)
        return geom, CRS.from_epsg(4326)
    except Exception:
        pass

    raise RuntimeError(f"Unsupported AOI format: {aoi_path}")


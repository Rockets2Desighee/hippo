
# import json
# import click
# from shapely.geometry import mapping
# from rasterio.warp import transform_geom
# from sat_ingest.core.search import SearchParams
# from sat_ingest.core.support_matrix import SupportMatrix
# from sat_ingest.core.adapter_registry import build_adapter
# from sat_ingest.utils.geometry import load_aoi_geometry

# _COLLECTION_HINTS = {
#     ("sentinel-2", "L2A"): ["sentinel-2-l2a"],
#     ("landsat-8",  "L2"):  ["landsat-c2-l2"],
#     ("landsat-9",  "L2"):  ["landsat-c2-l2"],
# }

# @click.command()
# @click.option("--collections", multiple=True)
# @click.option("--satellite")
# @click.option("--product")
# @click.option("--source")
# @click.option("--time")
# @click.option("--bbox")
# @click.option("--limit", type=int, default=10)
# @click.option("--aoi", help="Path to AOI file")
# @click.option("--explain", is_flag=True)
# def search_cmd(collections, satellite, product, source, time, bbox, limit, aoi, explain):
#     # Resolve adapter
#     if source:
#         adapter_name, reason = source, "source explicitly provided"
#     elif satellite:
#         choice = SupportMatrix().resolve(satellite, product)
#         adapter_name, reason = choice.adapter, choice.reason
#     else:
#         adapter_name, reason = "stac_generic", "defaulted to STAC"

#     collections_list = list(collections) or None
#     if adapter_name == "stac_generic" and not collections_list:
#         collections_list = _COLLECTION_HINTS.get((satellite, product))

#     click.echo(f"[adapter] {adapter_name} — {reason}")
#     if explain:
#         click.echo(json.dumps({
#             "adapter": adapter_name,
#             "reason": reason,
#             "satellite": satellite,
#             "product": product,
#             "collections": collections_list,
#         }))

#     adapter = build_adapter(adapter_name)
#     bbox_list = [float(x) for x in bbox.split(",")] if bbox else None

#     intersects = None
#     if aoi:
#         geom, crs = load_aoi_geometry(aoi)
#         intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

#     params = SearchParams(
#         collections=collections_list,
#         time=time,
#         bbox=bbox_list,
#         intersects=intersects,
#         limit=limit,
#     )

#     for item in adapter.search(params):
#         click.echo(json.dumps({
#             "id": item.id,
#             "collection": item.collection,
#             "datetime": item.datetime,
#         }))




import click
import json
from shapely.geometry import mapping
from sat_ingest.core.search import SearchParams
from sat_ingest.core.support_matrix import SupportMatrix
from sat_ingest.core.adapter_registry import build_adapter
from sat_ingest.utils.geometry import load_aoi_geometry


_COLLECTION_HINTS = {
    ("sentinel-2", "L2A"): ["sentinel-2-l2a"],
    ("landsat-8",  "L2"):  ["landsat-c2-l2"],
    ("landsat-9",  "L2"):  ["landsat-c2-l2"],
}

def _maybe_infer_collections(satellite: str | None, product: str | None) -> list[str] | None:
    if not satellite:
        return None
    key = (satellite.lower(), product.upper() if product else None)
    return _COLLECTION_HINTS.get(key)

@click.command()
@click.option("--collections", multiple=True, help="STAC collections (used when source is STAC).")
@click.option("--satellite", help="e.g. sentinel-2, landsat-8, goes-16")
@click.option("--product", help="e.g. L2A, L2, etc.")
@click.option("--source", help="Override adapter (e.g., stac_generic, noaa_goes).")
@click.option("--time", help="ISO range or RFC3339, e.g. 2025-08-01/2025-08-08")
@click.option("--bbox", help="minx,miny,maxx,maxy")
@click.option("--limit", type=int, default=10)
@click.option("--aoi", help="Path to AOI file (.geojson, .json, .shp, .kml, .wkt)")
@click.option("--explain", is_flag=True, help="Print full JSON detail on adapter selection.")
def search_cmd(collections, satellite, product, source, time, bbox, limit, aoi, explain):
    if source:
        adapter_name = source
        reason = "source explicitly provided via --source"
    elif satellite:
        choice = SupportMatrix().resolve(satellite, product)
        adapter_name = choice.adapter
        reason = choice.reason
    else:
        adapter_name = "stac_generic"
        reason = "defaulted to STAC (no --source/--satellite provided)"

    collections_list = list(collections) or None
    if adapter_name == "stac_generic" and not collections_list:
        inferred = _maybe_infer_collections(satellite, product)
        if inferred:
            collections_list = inferred

    click.echo(f"[adapter] {adapter_name} — {reason}")
    if explain:
        click.echo(json.dumps({
            "adapter": adapter_name,
            "reason": reason,
            "satellite": satellite,
            "product": product,
            "collections": collections_list,
        }))

    adapter = build_adapter(adapter_name)
    bbox_list = [float(x) for x in bbox.split(",")] if bbox else None

    intersects = None
    if aoi:
        geom, crs = load_aoi_geometry(aoi)
        from rasterio.warp import transform_geom
        intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

    params = SearchParams(
        collections=collections_list,
        time=time,
        bbox=bbox_list,
        intersects=intersects,
        limit=limit,
    )

    for item in adapter.search(params):
        click.echo(json.dumps({
            "id": item.id,
            "collection": item.collection,
            "datetime": item.datetime,
        }))



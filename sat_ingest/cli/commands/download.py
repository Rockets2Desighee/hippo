
# import click
# from shapely.geometry import mapping
# from rasterio.warp import transform_geom
# from sat_ingest.core.search import SearchParams
# from sat_ingest.core.support_matrix import SupportMatrix
# from sat_ingest.core.adapter_registry import build_adapter
# from sat_ingest.utils.geometry import load_aoi_geometry

# @click.command()
# @click.option("--collections", multiple=True)
# @click.option("--satellite")
# @click.option("--product")
# @click.option("--source")
# @click.option("--time", required=True)
# @click.option("--bbox")
# @click.option("--aoi")
# @click.option("--limit", type=int, default=1)
# @click.option("--assets")
# @click.option("--prefer-jp2", is_flag=True, default=False)
# @click.option("--prefer-cog", is_flag=True, default=False)
# @click.option("--data-root")
# @click.option("--explain", is_flag=True)
# def download_cmd(collections, satellite, product, source, time, bbox, aoi, limit, assets, prefer_jp2, prefer_cog, data_root, explain):
#     # Resolve adapter
#     if source:
#         adapter_name, reason = source, "source explicitly provided"
#     elif satellite:
#         choice = SupportMatrix().resolve(satellite, product)
#         adapter_name, reason = choice.adapter, getattr(choice, "reason", "resolved by Support Matrix")
#         collections = list(choice.collections) if choice.collections else collections
#     else:
#         adapter_name, reason = "stac_generic", "defaulted to STAC"

#     effective_collections = list(collections) or None
#     adapter = build_adapter(adapter_name, data_root=data_root)
#     click.echo(f"[adapter] {adapter_name} — {reason}")

#     bbox_list = [float(x) for x in bbox.split(",")] if bbox else None
#     asset_keys = [a.strip() for a in assets.split(",")] if assets else None

#     intersects = None
#     if aoi:
#         geom, crs = load_aoi_geometry(aoi)
#         intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

#     params = SearchParams(
#         collections=effective_collections,
#         time=time,
#         bbox=bbox_list,
#         intersects=intersects,
#         limit=limit,
#     )

#     for item in adapter.search(params):
#         result = adapter.download(item, asset_keys=asset_keys, prefer_jp2=prefer_jp2, prefer_cog=prefer_cog) or {}
#         if not result:
#             click.echo(f"No assets downloaded for item {item.id}")
#             continue
#         for k, asset in result.items():
#             click.echo(f"Downloaded {k} -> {asset.local_path}")




import click
from shapely.geometry import mapping
from sat_ingest.core.search import SearchParams
from sat_ingest.core.support_matrix import SupportMatrix
from sat_ingest.core.adapter_registry import build_adapter
from sat_ingest.utils.geometry import load_aoi_geometry


@click.command()
@click.option("--collections", multiple=True, help="STAC collections (used when source is STAC).")
@click.option("--satellite", help="e.g. sentinel-2, landsat-8, goes-16")
@click.option("--product", help="e.g. L2A, L2, etc.")
@click.option("--source", help="Override adapter (e.g., stac_generic, noaa_goes).")
@click.option("--time", required=True, help="ISO-8601 range or date (YYYY-MM-DD), e.g. 2024-07-01/2024-07-02")
@click.option("--bbox", required=False, help="minx,miny,maxx,maxy")
@click.option("--aoi", required=False, help="Path to AOI file (.geojson, .json, .shp, .kml, .wkt) to spatially filter results.")
@click.option("--limit", type=int, default=1, help="Max number of items to download.")
@click.option("--assets", help="Comma-separated asset keys (default: all assets).")
@click.option("--prefer-jp2", is_flag=True, default=False, help="Prefer JPEG2000 assets when aliases resolve to multiple candidates.")
@click.option("--prefer-cog", is_flag=True, default=False, help="Prefer Cloud-Optimized GeoTIFF assets when available.")
@click.option("--data-root", help="Destination directory. Defaults to ./data if not set via SAT_DATA_ROOT.")
@click.option("--explain", is_flag=True, help="Explain which adapter/source was selected and why.")
def download_cmd(collections, satellite, product, source, time, bbox, aoi, limit, assets, prefer_jp2, prefer_cog, data_root, explain):
    reason = None
    chosen_collections = None
    if source:
        adapter_name = source
        reason = "source explicitly provided via --source"
    elif satellite:
        choice = SupportMatrix().resolve(satellite, product)
        adapter_name = choice.adapter
        reason = getattr(choice, "reason", None) or "resolved by Support Matrix"
        chosen_collections = list(choice.collections) if choice.collections else None
    else:
        adapter_name = "stac_generic"
        reason = "defaulted to STAC (no --source/--satellite provided)"

    effective_collections = list(collections) or chosen_collections
    adapter = build_adapter(adapter_name, data_root=data_root)

    click.echo(f"[adapter] {adapter_name} — {reason}")

    bbox_list = [float(x) for x in bbox.split(",")] if bbox else None
    asset_keys = [a.strip() for a in assets.split(",")] if assets else None

    intersects = None
    if aoi:
        geom, crs = load_aoi_geometry(aoi)
        from rasterio.warp import transform_geom
        # Convert AOI to GeoJSON dict in EPSG:4326 so it's JSON serializable
        intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

    params = SearchParams(
        collections=effective_collections,
        time=time,
        bbox=bbox_list,
        intersects=intersects,
        limit=limit
    )
    

    for item in adapter.search(params):
        result = adapter.download(
            item,
            asset_keys=asset_keys,
            prefer_jp2=prefer_jp2,
            prefer_cog=prefer_cog,
        ) or {}

        if not result:
            click.echo(f"No assets downloaded for item {item.id}")
            continue

        for k, asset in result.items():
            click.echo(f"Downloaded {k} -> {asset.local_path}")

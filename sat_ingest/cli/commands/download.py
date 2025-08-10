# # THIS WORKS FOR V1.0


# import click
# from shapely.geometry import mapping
# from sat_ingest.core.search import SearchParams
# from sat_ingest.core.support_matrix import SupportMatrix
# from sat_ingest.core.adapter_registry import build_adapter
# from sat_ingest.utils.geometry import load_aoi_geometry


# @click.command()
# @click.option("--collections", multiple=True, help="STAC collections (used when source is STAC).")
# @click.option("--satellite", help="e.g. sentinel-2, landsat-8, goes-16")
# @click.option("--product", help="e.g. L2A, L2, etc.")
# @click.option("--source", help="Override adapter (e.g., stac_generic, noaa_goes).")
# @click.option("--time", required=True, help="ISO-8601 range or date (YYYY-MM-DD), e.g. 2024-07-01/2024-07-02")
# @click.option("--bbox", required=False, help="minx,miny,maxx,maxy")
# @click.option("--aoi", required=False, help="Path to AOI file (.geojson, .json, .shp, .kml, .wkt) to spatially filter results.")
# @click.option("--limit", type=int, default=1, help="Max number of items to download.")
# @click.option("--assets", help="Comma-separated asset keys (default: all assets).")
# @click.option("--prefer-jp2", is_flag=True, default=False, help="Prefer JPEG2000 assets when aliases resolve to multiple candidates.")
# @click.option("--prefer-cog", is_flag=True, default=False, help="Prefer Cloud-Optimized GeoTIFF assets when available.")
# @click.option("--data-root", help="Destination directory. Defaults to ./data if not set via SAT_DATA_ROOT.")
# @click.option("--explain", is_flag=True, help="Explain which adapter/source was selected and why.")
# def download_cmd(collections, satellite, product, source, time, bbox, aoi, limit, assets, prefer_jp2, prefer_cog, data_root, explain):
#     reason = None
#     chosen_collections = None
#     if source:
#         adapter_name = source
#         reason = "source explicitly provided via --source"
#     elif satellite:
#         choice = SupportMatrix().resolve(satellite, product)
#         adapter_name = choice.adapter
#         reason = getattr(choice, "reason", None) or "resolved by Support Matrix"
#         chosen_collections = list(choice.collections) if choice.collections else None
#     else:
#         adapter_name = "stac_generic"
#         reason = "defaulted to STAC (no --source/--satellite provided)"

#     effective_collections = list(collections) or chosen_collections
#     adapter = build_adapter(adapter_name, data_root=data_root)

#     click.echo(f"[adapter] {adapter_name} — {reason}")

#     bbox_list = [float(x) for x in bbox.split(",")] if bbox else None
#     asset_keys = [a.strip() for a in assets.split(",")] if assets else None

#     intersects = None
#     if aoi:
#         geom, crs = load_aoi_geometry(aoi)
#         from rasterio.warp import transform_geom
#         # Convert AOI to GeoJSON dict in EPSG:4326 so it's JSON serializable
#         intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

#     params = SearchParams(
#         collections=effective_collections,
#         time=time,
#         bbox=bbox_list,
#         intersects=intersects,
#         limit=limit
#     )
    

#     for item in adapter.search(params):
#         result = adapter.download(
#             item,
#             asset_keys=asset_keys,
#             prefer_jp2=prefer_jp2,
#             prefer_cog=prefer_cog,
#         ) or {}

#         if not result:
#             click.echo(f"No assets downloaded for item {item.id}")
#             continue

#         for k, asset in result.items():
#             click.echo(f"Downloaded {k} -> {asset.local_path}")





#####################################
# support S1, S2, S3, S5P, Landsat, and GOES in the same fallback system
#####################################

# import click
# from shapely.geometry import mapping
# from rasterio.warp import transform_geom
# from sat_ingest.core.search import SearchParams
# from sat_ingest.core.support_matrix import SupportMatrix
# from sat_ingest.utils.geometry import load_aoi_geometry
# from ._fallback import run_with_fallback

# BAND_ALIASES = {
#     "red": ["B04", "red"],
#     "green": ["B03", "green"],
#     "blue": ["B02", "blue"]
# }

# @click.command()
# @click.option("--collections", multiple=True)
# @click.option("--satellite")
# @click.option("--product")
# @click.option("--source")
# @click.option("--fallback-order")
# @click.option("--auto-fallback", is_flag=True, default=False)
# @click.option("--time", required=True)
# @click.option("--bbox")
# @click.option("--aoi")
# @click.option("--limit", type=int, default=1)
# @click.option("--assets")
# @click.option("--prefer-jp2", is_flag=True, default=False)
# @click.option("--prefer-cog", is_flag=True, default=False)
# @click.option("--data-root")
# @click.option("--explain", is_flag=True)
# def download_cmd(collections, satellite, product, source, fallback_order, auto_fallback,
#                  time, bbox, aoi, limit, assets, prefer_jp2, prefer_cog, data_root, explain):
#     chosen_collections = None
#     reason = None
#     if source:
#         adapter_name = source
#         reason = "source explicitly provided via --source"
#     elif satellite:
#         choice = SupportMatrix().resolve(satellite, product)
#         adapter_name = choice.adapter
#         reason = choice.reason
#         chosen_collections = list(choice.collections) if choice.collections else None
#     else:
#         adapter_name = "stac_generic"
#         reason = "defaulted to STAC"

#     if explain:
#         click.echo({"adapter": adapter_name, "reason": reason})

#     effective_collections = list(collections) or chosen_collections

#     bbox_list = [float(x) for x in bbox.split(",")] if bbox else None
#     intersects = None
#     if aoi:
#         geom, crs = load_aoi_geometry(aoi)
#         intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

#     # Per-band alias resolution
#     asset_keys = None
#     if assets:
#         requested = [a.strip() for a in assets.split(",")]
#         resolved = []
#         for band in requested:
#             resolved.extend(BAND_ALIASES.get(band, [band]))
#         asset_keys = resolved

#     params = SearchParams(
#         collections=effective_collections,
#         time=time,
#         bbox=bbox_list,
#         intersects=intersects,
#         limit=limit
#     )

#     run_with_fallback(
#         initial_source=adapter_name,
#         params=params,
#         fallback_order=fallback_order,
#         auto_fallback=auto_fallback,
#         op_name="download",
#         op_kwargs={
#             "asset_keys": asset_keys,
#             "prefer_jp2": prefer_jp2,
#             "prefer_cog": prefer_cog,
#             "data_root": data_root
#         }
#     )



##########################################

# THIS WORKS FOR ALL ADAPTERS AND SATELLITES
# WITH PLACEHOLDERS

###########################################


# # sat_ingest/cli/commands/download.py
# import click
# from ._fallback import run_with_fallback

# BAND_ALIASES = {
#     "red": ["B04", "B4", "red"],
#     "green": ["B03", "B3", "green"],
#     "blue": ["B02", "B2", "blue"],
# }

# @click.command("download")
# @click.option("--satellite", required=True)
# @click.option("--product", required=True)
# @click.option("--source", help="Preferred data source adapter")
# @click.option("--fallback-order", help="Comma-separated list of adapters to try in order")
# @click.option("--auto-fallback", is_flag=True)
# @click.option("--time")
# @click.option("--limit", type=int)
# @click.option("--aoi")
# @click.option("--assets", help="Comma-separated list of asset names")
# @click.option("--prefer-cog", is_flag=True)
# def download_cmd(satellite, product, source, fallback_order, auto_fallback, time, limit, aoi, assets, prefer_cog):
#     """Download assets with per-band alias mapping and fallback."""
#     if assets:
#         assets_list = []
#         for asset in assets.split(","):
#             asset = asset.strip().lower()
#             assets_list.append(BAND_ALIASES.get(asset, [asset]))
#     else:
#         assets_list = None

#     def run_download(adapter_client):
#         return adapter_client.download(
#             satellite=satellite,
#             product=product,
#             time=time,
#             limit=limit,
#             aoi=aoi,
#             assets=assets_list,
#             prefer_cog=prefer_cog
#         )

#     run_with_fallback(
#         satellite, product, source, fallback_order, auto_fallback, run_download
#     )


















############################
# THIS IS FOR CDSE STAC
############################


import click
from shapely.geometry import mapping
from sat_ingest.core.search import SearchParams
from sat_ingest.core.support_matrix import SupportMatrix
from sat_ingest.utils.geometry import load_aoi_geometry
from ._fallback import run_with_fallback
from pathlib import Path
from typing import Sequence, Optional
from PIL import Image
import warnings
from PIL import Image as PILImage

# Suppress Pillow's large image warning
warnings.simplefilter("ignore", Image.DecompressionBombWarning)

# Alias map for each logical band
BAND_ALIASES = {
    "red": ["red", "B04", "visual"],
    "green": ["green", "B03", "visual"],
    "blue": ["blue", "B02", "visual"],
}

def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
    """Find a band file in the given directory or its subdirectories by aliases."""
    for p in item_dir.rglob("*"):
        if p.is_file():
            stem = p.stem.lower()
            name = p.name.lower()
            for n in names:
                if stem == n.lower() or name.startswith(n.lower()):
                    return p
    return None

@click.command()
@click.option("--collections", multiple=True)
@click.option("--satellite")
@click.option("--product")
@click.option("--source")
@click.option("--time", required=True)
@click.option("--bbox")
@click.option("--aoi")
@click.option("--limit", type=int, default=1)
@click.option("--assets")
@click.option("--prefer-jp2", is_flag=True, default=False)
@click.option("--prefer-cog", is_flag=True, default=False)
@click.option("--data-root")
@click.option("--explain", is_flag=True)
@click.option("--fallback-order", help="Comma-separated list of adapters to try on failure.")
@click.option("--auto-fallback", is_flag=True, help="Skip prompts and try next automatically.")
def download_cmd(collections, satellite, product, source, time, bbox, aoi, limit, assets,
                 prefer_jp2, prefer_cog, data_root, explain, fallback_order, auto_fallback):

    reason = None
    chosen_collections = None
    if source:
        adapter_name = source
        reason = "source explicitly provided via --source"
    elif satellite:
        choice = SupportMatrix().resolve(satellite, product)
        adapter_name = choice.adapter
        reason = choice.reason
        chosen_collections = list(choice.collections) if choice.collections else None
    else:
        adapter_name = "stac_generic"
        reason = "defaulted to STAC"

    effective_collections = list(collections) or chosen_collections

    if explain:
        click.echo(f"[adapter] {adapter_name} — {reason}")

    bbox_list = [float(x) for x in bbox.split(",")] if bbox else None

    asset_keys = None
    if assets:
        user_assets = [a.strip() for a in assets.split(",")]
        # Per-band alias mapping
        asset_keys = []
        for band in user_assets:
            if band in BAND_ALIASES:
                asset_keys.append(BAND_ALIASES[band])
            else:
                asset_keys.append([band])

    intersects = None
    if aoi:
        geom, crs = load_aoi_geometry(aoi)
        from rasterio.warp import transform_geom
        intersects = transform_geom(crs.to_string(), "EPSG:4326", mapping(geom))

    params = SearchParams(
        collections=effective_collections,
        time=time,
        bbox=bbox_list,
        intersects=intersects,
        limit=limit
    )

    def _runner(adapter, params, asset_keys, prefer_jp2, prefer_cog):
        for item in adapter.search(params):
            # Flatten for adapter download
            flat_keys = [alias for group in (asset_keys or []) for alias in group]
            result = adapter.download(item, asset_keys=flat_keys,
                                      prefer_jp2=prefer_jp2,
                                      prefer_cog=prefer_cog) or {}

            # Verify presence of at least one alias per requested band
            if asset_keys:
                for group in asset_keys:
                    found = False
                    for alias in group:
                        if _find_band_path(Path(result.get(alias, {}).get("local_path", "")).parent, [alias]):
                            found = True
                            break
                    if not found:
                        click.echo(f"Warning: Could not find any of {group} in downloaded files.")

            for k, asset in result.items():
                click.echo(f"Downloaded {k} -> {asset.local_path}")

    run_with_fallback(
        primary_adapter=adapter_name,
        func=_runner,
        func_kwargs={"params": params, "asset_keys": asset_keys,
                     "prefer_jp2": prefer_jp2, "prefer_cog": prefer_cog},
        satellite=satellite,
        product=product,
        fallback_order=[f.strip() for f in fallback_order.split(",")] if fallback_order else None,
        auto_fallback=auto_fallback
    )

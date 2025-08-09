# # THIS WORKS FOR V1.0


# from pathlib import Path
# from typing import Optional, Sequence
# import click
# import numpy as np
# from PIL import Image
# from shapely.geometry import mapping
# from sat_ingest.utils.geometry import load_aoi_geometry


# def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
#     """Find a file in item_dir that matches given names."""
#     candidates = []
#     for p in item_dir.iterdir():
#         if not p.is_file():
#             continue
#         stem = p.stem.lower()
#         name = p.name.lower()
#         if stem in [n.lower() for n in names] or any(name.startswith(n.lower()) for n in names):
#             candidates.append(p)
#     return candidates[0] if candidates else None


# def _read_gray(path: Path) -> np.ndarray:
#     im = Image.open(path)
#     arr = np.array(im)
#     if arr.ndim == 3:  # convert RGB to single channel
#         arr = np.mean(arr, axis=2)
#     return arr.astype(np.float32)


# def _percentile_stretch(x: np.ndarray, p_low: float = 2.0, p_high: float = 98.0) -> np.ndarray:
#     lo = np.percentile(x, p_low)
#     hi = np.percentile(x, p_high)
#     if hi <= lo:
#         hi, lo = x.max(), x.min()
#     x = np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
#     return (x * 255.0).astype(np.uint8)


# @click.command()
# @click.argument("item_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
# @click.option("--out", type=click.Path(dir_okay=False, path_type=Path), default=None,
#               help="Output PNG path (defaults to <item_dir>/quicklook.png).")
# @click.option("--assets", default="red,green,blue", help="Comma-separated asset keys to use as R,G,B.")
# @click.option("--size", type=int, default=1024, help="Max width/height of output PNG.")
# @click.option("--clip", type=float, default=2.0, help="Percentile clip (low/high).")
# @click.option("--aoi", type=click.Path(exists=True, dir_okay=False, path_type=Path),
#               help="Optional AOI file to spatially crop the quicklook.")
# @click.option("--buffer", type=float, default=0.01, help="Buffer AOI in degrees to avoid mostly black for tiny polygons.")
# def quicklook_cmd(item_dir: Path, out: Optional[Path], assets: str, size: int, clip: float,
#                   aoi: Optional[Path], buffer: float):
#     """
#     Create an RGB PNG quicklook for an already-downloaded item directory.
#     """
#     asset_list = [a.strip() for a in assets.split(",")]
#     if len(asset_list) != 3:
#         raise click.ClickException("--assets must specify exactly three bands (R,G,B)")

#     # Find bands
#     r_path = _find_band_path(item_dir, [asset_list[0]])
#     g_path = _find_band_path(item_dir, [asset_list[1]])
#     b_path = _find_band_path(item_dir, [asset_list[2]])
#     if not all([r_path, g_path, b_path]):
#         missing = [n for n, p in zip(asset_list, [r_path, g_path, b_path]) if p is None]
#         raise click.ClickException(f"Could not find bands in {item_dir}: {', '.join(missing)}")

#     # Read data
#     R = _read_gray(r_path)
#     G = _read_gray(g_path)
#     B = _read_gray(b_path)

#     H, W = min(R.shape[0], G.shape[0], B.shape[0]), min(R.shape[1], G.shape[1], B.shape[1])
#     R, G, B = R[:H, :W], G[:H, :W], B[:H, :W]
#     rgb = np.dstack([R, G, B])

#     if aoi:
#         geom, geom_crs = load_aoi_geometry(aoi)
#         if buffer:
#             geom = geom.buffer(buffer)

#         try:
#             import rasterio
#             from rasterio.features import geometry_mask
#             from rasterio.warp import transform_geom
#         except ImportError:
#             raise click.ClickException("rasterio is required for AOI cropping.")

#         with rasterio.open(r_path) as src:
#             target_crs = src.crs
#             geom_proj = transform_geom(geom_crs.to_string(), target_crs.to_string(), mapping(geom))
#             mask = geometry_mask([geom_proj], transform=src.transform, invert=True,
#                                  out_shape=(src.height, src.width))

#         mask = mask[:H, :W]
#         rgb[~mask] = 0

#         # Auto-scale AFTER masking so AOI area is enhanced
#         for i in range(3):
#             band = rgb[..., i]
#             band[mask] = _percentile_stretch(band[mask], p_low=clip, p_high=100 - clip)
#             rgb[..., i] = band
#     else:
#         # No AOI: just apply normal stretching
#         R = _percentile_stretch(R, p_low=clip, p_high=100 - clip)
#         G = _percentile_stretch(G, p_low=clip, p_high=100 - clip)
#         B = _percentile_stretch(B, p_low=clip, p_high=100 - clip)
#         rgb = np.dstack([R, G, B])

#     img = Image.fromarray(rgb.astype(np.uint8), mode="RGB")

#     if max(img.size) > size:
#         img.thumbnail((size, size))

#     out_path = out or (item_dir / "quicklook.png")
#     img.save(out_path, format="PNG")
#     click.echo(f"Wrote {out_path}")






# ########################################
# ########################################
# # THIS WAS MEANT TO WORK FOR NOAA QUICKLOOKS AS WELL, BUT I DON'T HAVE CREDENTIALS FOR NOW. 
# # WILL GET BACK TO THIS

# from pathlib import Path
# from typing import Optional, Sequence
# import click
# import numpy as np
# from PIL import Image
# import warnings
# from ._fallback import run_with_fallback

# # Suppress Pillow's decompression bomb warnings
# warnings.simplefilter("ignore", Image.DecompressionBombWarning)

# # Alias mapping for each logical band
# BAND_ALIASES = {
#     "red": ["red", "B04", "visual", "CMI_C02", "band02"],
#     "green": ["green", "B03", "visual", "synthetic_green"],
#     "blue": ["blue", "B02", "visual", "CMI_C01", "band01"],
# }

# # Special GOES mapping
# GOES_ALIASES = {
#     "red": ["CMI_C02", "band02", "B02", "red"],
#     "blue": ["CMI_C01", "band01", "B01", "blue"],
# }

# def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
#     """Find a band file in the given directory or its subdirectories by aliases."""
#     for p in item_dir.rglob("*"):
#         if p.is_file():
#             stem = p.stem.lower()
#             name = p.name.lower()
#             for n in names:
#                 if stem == n.lower() or name.startswith(n.lower()):
#                     return p
#     return None

# def _read_gray(path: Path) -> np.ndarray:
#     im = Image.open(path)
#     arr = np.array(im)
#     if arr.ndim == 3:
#         arr = np.mean(arr, axis=2)
#     return arr.astype(np.float32)

# def _percentile_stretch(x: np.ndarray, p_low=2.0, p_high=98.0) -> np.ndarray:
#     lo = np.percentile(x, p_low)
#     hi = np.percentile(x, p_high)
#     if hi <= lo:
#         hi, lo = x.max(), x.min()
#     x = np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
#     return (x * 255.0).astype(np.uint8)

# @click.command()
# @click.argument("item_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
# @click.option("--out", type=click.Path(dir_okay=False, path_type=Path), default=None)
# @click.option("--assets", default="red,green,blue")
# @click.option("--size", type=int, default=1024)
# @click.option("--clip", type=float, default=2.0)
# @click.option("--source")
# @click.option("--satellite")
# @click.option("--product")
# @click.option("--fallback-order", help="Comma-separated list of adapters to try on failure.")
# @click.option("--auto-fallback", is_flag=True, help="Skip prompts and try next automatically.")
# def quicklook_cmd(item_dir: Path, out: Optional[Path], assets: str, size: int, clip: float,
#                   source, satellite, product, fallback_order, auto_fallback):
#     """
#     Generate a quicklook PNG from three bands (default: red, green, blue).
#     Supports Sentinel-style RGB and NOAA GOES pseudo-RGB composites.
#     """
#     asset_list = [a.strip() for a in assets.split(",")]
#     if len(asset_list) != 3:
#         raise click.ClickException("--assets must specify exactly three bands")

#     def _runner(adapter, item_dir, out, assets, size, clip):
#         # Special handling for NOAA GOES
#         if satellite and satellite.lower() == "noaa-goes":
#             r_path = _find_band_path(item_dir, GOES_ALIASES["red"])
#             b_path = _find_band_path(item_dir, GOES_ALIASES["blue"])
#             if not r_path or not b_path:
#                 raise click.ClickException(f"Missing GOES bands in {item_dir}")

#             R = _percentile_stretch(_read_gray(r_path), p_low=clip, p_high=100 - clip)
#             B = _percentile_stretch(_read_gray(b_path), p_low=clip, p_high=100 - clip)
#             G = ((R.astype(np.float32) + B.astype(np.float32)) / 2).astype(np.uint8)  # synthetic green
#         else:
#             # Standard RGB workflow
#             r_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[0], [asset_list[0]]))
#             g_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[1], [asset_list[1]]))
#             b_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[2], [asset_list[2]]))

#             if not all([r_path, g_path, b_path]):
#                 raise click.ClickException(f"Missing one or more bands in {item_dir}")

#             R = _percentile_stretch(_read_gray(r_path), p_low=clip, p_high=100 - clip)
#             G = _percentile_stretch(_read_gray(g_path), p_low=clip, p_high=100 - clip)
#             B = _percentile_stretch(_read_gray(b_path), p_low=clip, p_high=100 - clip)

#         rgb = np.dstack([R, G, B])
#         img = Image.fromarray(rgb, mode="RGB")
#         if max(img.size) > size:
#             img.thumbnail((size, size))
#         out_path = out or (item_dir / "quicklook.png")
#         img.save(out_path, format="PNG")
#         click.echo(f"Wrote {out_path}")

#     run_with_fallback(
#         primary_adapter=source or "stac_generic",
#         func=_runner,
#         func_kwargs={"item_dir": item_dir, "out": out, "assets": assets,
#                      "size": size, "clip": clip},
#         satellite=satellite,
#         product=product,
#         fallback_order=[f.strip() for f in fallback_order.split(",")] if fallback_order else None,
#         auto_fallback=auto_fallback
#     )




###########################
###########################
# THIS WORKS FOR GENERIC_STAC + CDSE STAC + NOAA

from pathlib import Path
from typing import Optional, Sequence
import click
import numpy as np
from PIL import Image
from ._fallback import run_with_fallback

# Alias mapping for each logical band
BAND_ALIASES = {
    "red": ["red", "B04", "visual"],
    "green": ["green", "B03", "visual"],
    "blue": ["blue", "B02", "visual"],
}

def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
    """Find a band file in the given directory or its subdirectories by aliases."""
    # First check this directory
    for p in item_dir.iterdir():
        if p.is_file():
            stem = p.stem.lower()
            name = p.name.lower()
            for n in names:
                if stem == n.lower() or name.startswith(n.lower()):
                    return p
    # Then check subdirectories recursively
    for sub in item_dir.rglob("*"):
        if sub.is_file():
            stem = sub.stem.lower()
            name = sub.name.lower()
            for n in names:
                if stem == n.lower() or name.startswith(n.lower()):
                    return sub
    return None

def _read_gray(path: Path) -> np.ndarray:
    im = Image.open(path)
    arr = np.array(im)
    if arr.ndim == 3:
        arr = np.mean(arr, axis=2)
    return arr.astype(np.float32)

def _percentile_stretch(x: np.ndarray, p_low=2.0, p_high=98.0) -> np.ndarray:
    lo = np.percentile(x, p_low)
    hi = np.percentile(x, p_high)
    if hi <= lo:
        hi, lo = x.max(), x.min()
    x = np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
    return (x * 255.0).astype(np.uint8)

@click.command()
@click.argument("item_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--out", type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option("--assets", default="red,green,blue")
@click.option("--size", type=int, default=1024)
@click.option("--clip", type=float, default=2.0)
@click.option("--source")
@click.option("--satellite")
@click.option("--product")
@click.option("--fallback-order", help="Comma-separated list of adapters to try on failure.")
@click.option("--auto-fallback", is_flag=True, help="Skip prompts and try next automatically.")
def quicklook_cmd(item_dir: Path, out: Optional[Path], assets: str, size: int, clip: float,
                  source, satellite, product, fallback_order, auto_fallback):
    """
    Generate a quicklook PNG from three bands (default: red, green, blue).
    Automatically tries alias names (e.g., red -> B04 -> visual) and
    searches subdirectories until it finds matching band files.
    """
    asset_list = [a.strip() for a in assets.split(",")]
    if len(asset_list) != 3:
        raise click.ClickException("--assets must specify exactly three bands")

    def _runner(adapter, item_dir, out, assets, size, clip):
        r_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[0], [asset_list[0]]))
        g_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[1], [asset_list[1]]))
        b_path = _find_band_path(item_dir, BAND_ALIASES.get(asset_list[2], [asset_list[2]]))

        if not all([r_path, g_path, b_path]):
            raise click.ClickException(f"Missing one or more bands in {item_dir}")

        R = _percentile_stretch(_read_gray(r_path), p_low=clip, p_high=100 - clip)
        G = _percentile_stretch(_read_gray(g_path), p_low=clip, p_high=100 - clip)
        B = _percentile_stretch(_read_gray(b_path), p_low=clip, p_high=100 - clip)
        rgb = np.dstack([R, G, B])
        img = Image.fromarray(rgb, mode="RGB")
        if max(img.size) > size:
            img.thumbnail((size, size))
        out_path = out or (item_dir / "quicklook.png")
        img.save(out_path, format="PNG")
        click.echo(f"Wrote {out_path}")

    run_with_fallback(
        primary_adapter=source or "stac_generic",
        func=_runner,
        func_kwargs={"item_dir": item_dir, "out": out, "assets": assets,
                     "size": size, "clip": clip},
        satellite=satellite,
        product=product,
        fallback_order=[f.strip() for f in fallback_order.split(",")] if fallback_order else None,
        auto_fallback=auto_fallback
    )


# from pathlib import Path
# from typing import Optional, Sequence
# import click
# import numpy as np
# from PIL import Image
# from shapely.geometry import mapping
# from rasterio.warp import transform_geom
# from sat_ingest.utils.geometry import load_aoi_geometry

# def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
#     """Find a file in item_dir that matches any of the given names (case-insensitive)."""
#     for p in item_dir.iterdir():
#         if not p.is_file():
#             continue
#         stem = p.stem.lower()
#         name = p.name.lower()
#         if stem in [n.lower() for n in names] or any(name.startswith(n.lower()) for n in names):
#             return p
#     return None

# def _read_gray(path: Path) -> np.ndarray:
#     """Read an image and convert to float32 grayscale array."""
#     im = Image.open(path)
#     arr = np.array(im)
#     if arr.ndim == 3:  # RGB → grayscale
#         arr = np.mean(arr, axis=2)
#     return arr.astype(np.float32)

# def _percentile_stretch(x: np.ndarray, p_low: float = 2.0, p_high: float = 98.0) -> np.ndarray:
#     """Clip by percentiles and rescale to 0–255 uint8."""
#     lo = np.percentile(x, p_low)
#     hi = np.percentile(x, p_high)
#     if hi <= lo:
#         hi, lo = x.max(), x.min()
#     x = np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
#     return (x * 255.0).astype(np.uint8)

# @click.command()
# @click.argument("item_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
# @click.option("--out", type=click.Path(dir_okay=False, path_type=Path),
#               help="Output PNG path (defaults to <item_dir>/quicklook.png).")
# @click.option("--assets", default="red,green,blue", help="Comma-separated asset keys for R,G,B.")
# @click.option("--size", type=int, default=1024, help="Max width/height of output PNG.")
# @click.option("--clip", type=float, default=2.0, help="Percentile clip (low/high).")
# @click.option("--aoi", type=click.Path(exists=True, dir_okay=False, path_type=Path),
#               help="Optional AOI file to crop the quicklook.")
# @click.option("--buffer", type=float, default=0.01, help="Buffer AOI in degrees (avoid mostly black for small AOIs).")
# def quicklook_cmd(item_dir: Path, out: Optional[Path], assets: str, size: int, clip: float, aoi: Optional[Path], buffer: float):
#     """Create an RGB PNG quicklook for an already-downloaded item directory."""
#     asset_list = [a.strip() for a in assets.split(",")]
#     if len(asset_list) != 3:
#         raise click.ClickException("--assets must specify exactly three bands (R,G,B)")

#     # Find band files
#     r_path = _find_band_path(item_dir, [asset_list[0]])
#     g_path = _find_band_path(item_dir, [asset_list[1]])
#     b_path = _find_band_path(item_dir, [asset_list[2]])
#     if not all([r_path, g_path, b_path]):
#         missing = [n for n, p in zip(asset_list, [r_path, g_path, b_path]) if p is None]
#         raise click.ClickException(f"Could not find bands in {item_dir}: {', '.join(missing)}")

#     # Read & stretch
#     R = _percentile_stretch(_read_gray(r_path), p_low=clip, p_high=100 - clip)
#     G = _percentile_stretch(_read_gray(g_path), p_low=clip, p_high=100 - clip)
#     B = _percentile_stretch(_read_gray(b_path), p_low=clip, p_high=100 - clip)

#     # Match dimensions
#     H = min(R.shape[0], G.shape[0], B.shape[0])
#     W = min(R.shape[1], G.shape[1], B.shape[1])
#     R, G, B = R[:H, :W], G[:H, :W], B[:H, :W]
#     rgb = np.dstack([R, G, B])

#     # AOI crop if requested
#     if aoi:
#         geom, geom_crs = load_aoi_geometry(aoi)

#         # Auto-scale buffer: bigger for smaller polygons
#         bounds = geom.bounds  # (minx, miny, maxx, maxy)
#         diag_deg = ((bounds[2] - bounds[0])**2 + (bounds[3] - bounds[1])**2) ** 0.5
#         auto_buffer = max(0.01, min(0.1, 0.02 / diag_deg))  # clamp between 0.01 and 0.1
#         geom = geom.buffer(auto_buffer)

#         try:
#             import rasterio
#             from rasterio.features import geometry_mask
#             from rasterio.warp import transform_geom
#         except ImportError:
#             raise click.ClickException("rasterio is required for AOI cropping.")

#         with rasterio.open(r_path) as src:
#             target_crs = src.crs
#             geom_proj = transform_geom(geom_crs.to_string(), target_crs.to_string(), geom.__geo_interface__)
#             mask = geometry_mask([geom_proj], transform=src.transform, invert=True, out_shape=(src.height, src.width))

#         mask = mask[:H, :W]
#         rgb[~mask] = 0
#         img = Image.fromarray(rgb, mode="RGB")


#     out_path = out or (item_dir / "quicklook.png")
#     img.save(out_path, format="PNG")
#     click.echo(f"Wrote {out_path}")



from pathlib import Path
from typing import Optional, Sequence
import click
import numpy as np
from PIL import Image
from shapely.geometry import mapping
from sat_ingest.utils.geometry import load_aoi_geometry


def _find_band_path(item_dir: Path, names: Sequence[str]) -> Optional[Path]:
    """Find a file in item_dir that matches given names."""
    candidates = []
    for p in item_dir.iterdir():
        if not p.is_file():
            continue
        stem = p.stem.lower()
        name = p.name.lower()
        if stem in [n.lower() for n in names] or any(name.startswith(n.lower()) for n in names):
            candidates.append(p)
    return candidates[0] if candidates else None


def _read_gray(path: Path) -> np.ndarray:
    im = Image.open(path)
    arr = np.array(im)
    if arr.ndim == 3:  # convert RGB to single channel
        arr = np.mean(arr, axis=2)
    return arr.astype(np.float32)


def _percentile_stretch(x: np.ndarray, p_low: float = 2.0, p_high: float = 98.0) -> np.ndarray:
    lo = np.percentile(x, p_low)
    hi = np.percentile(x, p_high)
    if hi <= lo:
        hi, lo = x.max(), x.min()
    x = np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
    return (x * 255.0).astype(np.uint8)


@click.command()
@click.argument("item_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--out", type=click.Path(dir_okay=False, path_type=Path), default=None,
              help="Output PNG path (defaults to <item_dir>/quicklook.png).")
@click.option("--assets", default="red,green,blue", help="Comma-separated asset keys to use as R,G,B.")
@click.option("--size", type=int, default=1024, help="Max width/height of output PNG.")
@click.option("--clip", type=float, default=2.0, help="Percentile clip (low/high).")
@click.option("--aoi", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Optional AOI file to spatially crop the quicklook.")
@click.option("--buffer", type=float, default=0.01, help="Buffer AOI in degrees to avoid mostly black for tiny polygons.")
def quicklook_cmd(item_dir: Path, out: Optional[Path], assets: str, size: int, clip: float,
                  aoi: Optional[Path], buffer: float):
    """
    Create an RGB PNG quicklook for an already-downloaded item directory.
    """
    asset_list = [a.strip() for a in assets.split(",")]
    if len(asset_list) != 3:
        raise click.ClickException("--assets must specify exactly three bands (R,G,B)")

    # Find bands
    r_path = _find_band_path(item_dir, [asset_list[0]])
    g_path = _find_band_path(item_dir, [asset_list[1]])
    b_path = _find_band_path(item_dir, [asset_list[2]])
    if not all([r_path, g_path, b_path]):
        missing = [n for n, p in zip(asset_list, [r_path, g_path, b_path]) if p is None]
        raise click.ClickException(f"Could not find bands in {item_dir}: {', '.join(missing)}")

    # Read data
    R = _read_gray(r_path)
    G = _read_gray(g_path)
    B = _read_gray(b_path)

    H, W = min(R.shape[0], G.shape[0], B.shape[0]), min(R.shape[1], G.shape[1], B.shape[1])
    R, G, B = R[:H, :W], G[:H, :W], B[:H, :W]
    rgb = np.dstack([R, G, B])

    if aoi:
        geom, geom_crs = load_aoi_geometry(aoi)
        if buffer:
            geom = geom.buffer(buffer)

        try:
            import rasterio
            from rasterio.features import geometry_mask
            from rasterio.warp import transform_geom
        except ImportError:
            raise click.ClickException("rasterio is required for AOI cropping.")

        with rasterio.open(r_path) as src:
            target_crs = src.crs
            geom_proj = transform_geom(geom_crs.to_string(), target_crs.to_string(), mapping(geom))
            mask = geometry_mask([geom_proj], transform=src.transform, invert=True,
                                 out_shape=(src.height, src.width))

        mask = mask[:H, :W]
        rgb[~mask] = 0

        # Auto-scale AFTER masking so AOI area is enhanced
        for i in range(3):
            band = rgb[..., i]
            band[mask] = _percentile_stretch(band[mask], p_low=clip, p_high=100 - clip)
            rgb[..., i] = band
    else:
        # No AOI: just apply normal stretching
        R = _percentile_stretch(R, p_low=clip, p_high=100 - clip)
        G = _percentile_stretch(G, p_low=clip, p_high=100 - clip)
        B = _percentile_stretch(B, p_low=clip, p_high=100 - clip)
        rgb = np.dstack([R, G, B])

    img = Image.fromarray(rgb.astype(np.uint8), mode="RGB")

    if max(img.size) > size:
        img.thumbnail((size, size))

    out_path = out or (item_dir / "quicklook.png")
    img.save(out_path, format="PNG")
    click.echo(f"Wrote {out_path}")



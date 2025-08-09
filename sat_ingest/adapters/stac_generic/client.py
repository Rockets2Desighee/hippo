

from __future__ import annotations
from typing import Iterable, Optional, Sequence, Dict, List
from sat_ingest.core.adapters.base import CatalogAdapter
from sat_ingest.core.search import SearchParams
from sat_ingest.core.models import Item, Asset
from sat_ingest.core.http import HttpClient
from sat_ingest.core.storage.local import LocalSink

from .mapper import map_stac_item
import os
import tempfile
import sys
from urllib.parse import urlparse
from tqdm import tqdm


# Band alias map: prefer non-jp2 names first
ALIAS_MAP: dict[str, list[str]] = {
    "B02": ["blue", "B02", "blue-jp2", "B02_JP2"],
    "B03": ["green", "B03", "green-jp2", "B03_JP2"],
    "B04": ["red", "B04", "red-jp2", "B04_JP2"],
    "B08": ["nir", "nir08", "B08", "nir08-jp2", "B08_JP2"],
}


# Default STAC endpoint (Earth Search). Override with STAC_URL env if desired.
STAC_DEFAULT_URL = os.environ.get("STAC_URL", "https://earth-search.aws.element84.com/v1")


class StacGenericAdapter(CatalogAdapter):
    name = "Generic STAC"

    def __init__(self, base_url: str | None = None, data_root: str | None = None):
        """
        base_url: STAC API root. Defaults to Earth Search.
        data_root: Optional local destination root. If None, LocalSink uses SAT_DATA_ROOT or ./data.
        """
        self.base_url = base_url or STAC_DEFAULT_URL
        self.http = HttpClient()
        self.sink = LocalSink(root=data_root)

    # -----------------------------
    # Helpers
    # -----------------------------
    def _resolve_asset_key(self, item: Item, key: str) -> Optional[str]:
        """Map user-specified key (e.g., B04) to a real asset key present on the item (e.g., red)."""
        candidates = [key, key.lower()]
        candidates += ALIAS_MAP.get(key.upper(), [])
        for cand in candidates:
            if cand in item.assets:
                return cand
        return None

    def _extract_next_href(self, links: List[dict]) -> Optional[str]:
        for l in links or []:
            if l.get("rel") == "next" and l.get("href"):
                return l["href"]
        return None

    def _guess_extension(self, asset: Asset) -> str:
        """
        Pick a useful filename extension based on media_type, with a fallback to the URL path.
        Returns a string that *includes* the leading dot (".tif") or "" if unknown.
        """
        mt = (asset.media_type or "").lower()

        # Common GeoTIFF variants
        if "geotiff" in mt or "tiff" in mt:
            return ".tif"
        # JPEG2000
        if "jp2" in mt or "jpeg2000" in mt:
            return ".jp2"
        # Other common image types if ever present
        if "png" in mt:
            return ".png"
        if "jpeg" in mt or "jpg" in mt:
            return ".jpg"

        # Fallback: look at the URL path
        try:
            path = urlparse(asset.href).path
            _, ext = os.path.splitext(path)
            return ext if ext else ""
        except Exception:
            return ""

    # -----------------------------
    # Public API
    # -----------------------------
    def search(self, params: SearchParams) -> Iterable[Item]:
        """
        Streams across all pages by following links[rel='next'].
        Respects params.limit as a cap (if provided).
        """
        url = f"{self.base_url}/search"
        payload = params.to_stac_payload()
        remaining = payload.get("limit")

        # First page (POST)
        resp = self.http.post(url, json=payload).json()
        features = resp.get("features", [])
        for feat in features:
            if remaining is not None and remaining <= 0:
                return
            yield map_stac_item(feat)
            if remaining is not None:
                remaining -= 1

        # Follow next links (generic GET) until exhausted or hit remaining==0
        next_href = self._extract_next_href(resp.get("links", []))
        while next_href and (remaining is None or remaining > 0):
            page = self.http.get(next_href).json()
            for feat in page.get("features", []):
                if remaining is not None and remaining <= 0:
                    return
                yield map_stac_item(feat)
                if remaining is not None:
                    remaining -= 1
            next_href = self._extract_next_href(page.get("links", []))

    def item(self, item_id: str) -> Optional[Item]:
        """
        Fetch a single item by ID. Some STACs require collection in the path; try both styles.
        """
        url_with_glob = f"{self.base_url}/collections/*/items/{item_id}"
        url_plain = f"{self.base_url}/items/{item_id}"
        for candidate in (url_with_glob, url_plain):
            try:
                resp = self.http.get(candidate)
                return map_stac_item(resp.json())
            except Exception:
                continue
        return None

    def download(
        self,
        item: Item,
        asset_keys: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> Dict[str, Asset]:
        """
        Download selected assets for an item. Files are written via LocalSink:
        <DATA_ROOT>/<collection>/<item_id>/<asset_key>[.<ext>]
        """
        selected = asset_keys or list(item.assets.keys())
        out: Dict[str, Asset] = {}

        for requested_key in selected:
            actual_key = self._resolve_asset_key(item, requested_key)
            if actual_key is None:
                print(
                    f"Warning: asset '{requested_key}' not found on item {item.id}; skipping.",
                    file=sys.stderr,
                )
                continue

            asset = item.assets[actual_key]

            # Decide the on-disk filename (add extension if we can guess it)
            ext = self._guess_extension(asset)
            filename = f"{actual_key}{ext}"

            # Stream to a temp file first to avoid partial writes
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Per-asset progress bar that updates as bytes arrive.
                pbar = tqdm(
                    total=None,
                    unit="B",
                    unit_scale=True,
                    desc=f"{item.id}:{filename}",
                    leave=False,
                )

                def _on_chunk(n: int, total_bytes: int | None):
                    if total_bytes is not None and pbar.total is None:
                        pbar.total = total_bytes
                    pbar.update(n)

                # NOTE: requires HttpClient.stream_download supporting on_chunk callback
                self.http.stream_download(
                    asset.href,
                    tmp_path,
                    chunk_size=1024 * 512,
                    on_chunk=_on_chunk,
                )
                pbar.close()

                dest_key = f"{item.collection}/{item.id}/{filename}"
                dest_path = self.sink.put(tmp_path, dest_key)
                asset.local_path = dest_path
                out[actual_key] = asset
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        return out

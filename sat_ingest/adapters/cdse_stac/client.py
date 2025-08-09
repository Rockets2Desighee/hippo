# sat_ingest/adapters/cdse_stac/client.py
from __future__ import annotations
from typing import Iterable, Optional, Sequence, Dict, List
import os, sys, tempfile
from urllib.parse import urlparse

from sat_ingest.core.adapters.base import CatalogAdapter
from sat_ingest.core.search import SearchParams
from sat_ingest.core.models import Item, Asset
from sat_ingest.core.http import HttpClient
from sat_ingest.core.storage.local import LocalSink

from .token import TokenProvider

# Default CDSE STAC (override with CDSE_STAC_URL)
CDSE_STAC_URL = os.environ.get(
    "CDSE_STAC_URL",
    "https://catalogue.dataspace.copernicus.eu/stac"
)

# CDSE items commonly expose Sentinel-2 bands under B02/3/4, sometimes "visual".
# Map our UX-friendly keys to real asset keys found on the item.
ALIAS_MAP: dict[str, list[str]] = {
    # RGB convenience → raw S2 band IDs
    "red":   ["B04", "b04", "visual", "red"],
    "green": ["B03", "b03", "visual", "green"],
    "blue":  ["B02", "b02", "visual", "blue"],
    # Still accept band IDs directly
    "B04": ["B04", "red", "visual"],
    "B03": ["B03", "green", "visual"],
    "B02": ["B02", "blue", "visual"],
}

def _extract_next_href(links: List[dict]) -> Optional[str]:
    for l in links or []:
        if l.get("rel") == "next" and l.get("href"):
            return l["href"]
    return None

class CdseStacAdapter(CatalogAdapter):
    name = "CDSE STAC"

    def __init__(self, base_url: str | None = None, data_root: str | None = None):
        self.base_url = (base_url or CDSE_STAC_URL).rstrip("/")
        self.tokens = TokenProvider()
        # Attach bearer on all requests (search, item, and asset GET if needed)
        self.http = HttpClient(headers={"Authorization": f"Bearer {self.tokens.get_access_token()}"})
        self.sink = LocalSink(root=data_root)

    # ------------ helpers ------------
    def _resolve_asset_key(self, item: Item, requested: str) -> Optional[str]:
        cands = [requested, requested.lower()]
        cands += ALIAS_MAP.get(requested.upper(), [])
        cands += ALIAS_MAP.get(requested.lower(), [])
        for k in cands:
            if k in item.assets:
                return k
        return None

    def _guess_ext(self, asset: Asset) -> str:
        mt = (asset.media_type or "").lower()
        if "geotiff" in mt or "tiff" in mt: return ".tif"
        if "jp2" in mt or "jpeg2000" in mt: return ".jp2"
        from os.path import splitext
        _, ext = splitext(urlparse(asset.href).path)
        return ext or ""

    # ------------ public API ------------
    def search(self, params: SearchParams) -> Iterable[Item]:
        url = f"{self.base_url}/search"
        payload = params.to_stac_payload()
        remaining = payload.get("limit")

        resp = self.http.post(url, json=payload).json()
        for feat in resp.get("features", []):
            if remaining is not None and remaining <= 0:
                return
            from .mapper import map_stac_item   # reuse tiny mapper colocated below
            yield map_stac_item(feat)
            if remaining is not None:
                remaining -= 1

        next_href = _extract_next_href(resp.get("links", []))
        while next_href and (remaining is None or remaining > 0):
            page = self.http.get(next_href).json()
            for feat in page.get("features", []):
                if remaining is not None and remaining <= 0:
                    return
                from .mapper import map_stac_item
                yield map_stac_item(feat)
                if remaining is not None:
                    remaining -= 1
            next_href = _extract_next_href(page.get("links", []))

    def item(self, item_id: str) -> Optional[Item]:
        # Many STACs need collection in the path — try the wildcard first
        for candidate in (
            f"{self.base_url}/collections/*/items/{item_id}",
            f"{self.base_url}/items/{item_id}",
        ):
            try:
                from .mapper import map_stac_item
                return map_stac_item(self.http.get(candidate).json())
            except Exception:
                continue
        return None

    def download(self, item: Item, asset_keys: Optional[Sequence[str]] = None, **_) -> Dict[str, Asset]:
        selected = asset_keys or list(item.assets.keys())
        out: Dict[str, Asset] = {}

        for req in selected:
            actual = self._resolve_asset_key(item, req)
            if actual is None:
                print(f"Warning: asset '{req}' not found on {item.id}; skipping.", file=sys.stderr)
                continue

            a = item.assets[actual]
            ext = self._guess_ext(a)
            filename = f"{actual}{ext}"

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # The CDSE asset hrefs may require Authorization too — our HttpClient already carries it.
                self.http.stream_download(a.href, tmp_path, chunk_size=1024 * 512)
                dest_key = f"{item.collection}/{item.id}/{filename}"
                dest_path = self.sink.put(tmp_path, dest_key)
                a.local_path = dest_path
                out[actual] = a
            finally:
                try: os.remove(tmp_path)
                except OSError: pass

        return out

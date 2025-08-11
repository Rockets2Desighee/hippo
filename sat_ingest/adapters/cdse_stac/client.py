# sat_ingest/adapters/cdse_stac/client.py
from __future__ import annotations
from typing import Iterable, Optional, Sequence, Dict, List
import os, sys, tempfile, json
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

# Asset alias mapping for convenience keys
ALIAS_MAP: dict[str, list[str]] = {
    "red":   ["B04", "b04", "visual", "red"],
    "green": ["B03", "b03", "visual", "green"],
    "blue":  ["B02", "b02", "visual", "blue"],
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
        self.http = HttpClient(headers={"Authorization": f"Bearer {self.tokens.get_access_token()}"})
        self.sink = LocalSink(root=data_root)

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
        if "geotiff" in mt or "tiff" in mt:
            return ".tif"
        if "jp2" in mt or "jpeg2000" in mt:
            return ".jp2"
        from os.path import splitext
        _, ext = splitext(urlparse(asset.href).path)
        return ext or ""

    def search(self, params: SearchParams) -> Iterable[Item]:
        url = f"{self.base_url}/search"
        payload = {k: v for k, v in params.to_stac_payload().items()
                   if v not in (None, [], {}, '')}

        # CDSE requires certain fields
        if not payload.get("collections"):
            raise ValueError("CDSE STAC search requires at least one collection.")
        if not (payload.get("intersects") or payload.get("bbox")):
            raise ValueError("CDSE STAC search requires either 'intersects' or 'bbox'.")
        if "limit" not in payload:
            payload["limit"] = 100

        print(f"[cdse_stac] POST {url}")
        print(f"[cdse_stac] Payload:\n{json.dumps(payload, indent=2)}")

        resp = self.http.post(url, json=payload)
        if resp.status_code >= 400:
            try:
                print("[cdse_stac] Error details from CDSE:\n",
                      json.dumps(resp.json(), indent=2))
            except Exception:
                print("[cdse_stac] Error details from CDSE (raw):", resp.text)
            raise RuntimeError(
                f"CDSE STAC search failed: {resp.status_code} {resp.reason}"
            )

        data = resp.json()
        remaining = payload.get("limit")

        from .mapper import map_stac_item
        for feat in data.get("features", []):
            if remaining is not None and remaining <= 0:
                return
            yield map_stac_item(feat)
            if remaining is not None:
                remaining -= 1

        next_href = _extract_next_href(data.get("links", []))
        while next_href and (remaining is None or remaining > 0):
            page_resp = self.http.get(next_href)
            if page_resp.status_code >= 400:
                try:
                    print("[cdse_stac] Pagination error details:\n",
                          json.dumps(page_resp.json(), indent=2))
                except Exception:
                    print("[cdse_stac] Pagination error details (raw):", page_resp.text)
                raise RuntimeError(
                    f"CDSE STAC pagination failed: {page_resp.status_code} {page_resp.reason}"
                )
            page = page_resp.json()
            for feat in page.get("features", []):
                if remaining is not None and remaining <= 0:
                    return
                yield map_stac_item(feat)
                if remaining is not None:
                    remaining -= 1
            next_href = _extract_next_href(page.get("links", []))

    def item(self, item_id: str) -> Optional[Item]:
        from .mapper import map_stac_item
        for candidate in (
            f"{self.base_url}/collections/*/items/{item_id}",
            f"{self.base_url}/items/{item_id}",
        ):
            try:
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
                self.http.stream_download(a.href, tmp_path, chunk_size=1024 * 512)
                dest_key = f"{item.collection}/{item.id}/{filename}"
                dest_path = self.sink.put(tmp_path, dest_key)
                a.local_path = dest_path
                out[actual] = a
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        return out

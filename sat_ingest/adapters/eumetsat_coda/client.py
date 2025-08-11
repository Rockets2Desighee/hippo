from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional, List, Dict
import os
import sys

from sat_ingest.core.adapters.base import CatalogAdapter
from sat_ingest.core.search import SearchParams
from sat_ingest.core.models import Item, Asset
from sat_ingest.core.http import HttpClient
from sat_ingest.core.storage.local import LocalSink

from .token import TokenManager
from .mapper import map_coda_item

CODA_API = "https://coda.eumetsat.int/api/v1"


class EumetsatCodaAdapter(CatalogAdapter):
    name = "EUMETSAT CODA"

    def __init__(self, **kwargs):
        self.data_root = Path(kwargs.get("data_root") or os.environ.get("SAT_DATA_ROOT", "./data")).resolve()
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.http = HttpClient()
        self.sink = LocalSink(str(self.data_root))
        self.token_mgr = TokenManager()

    def _check_credentials(self):
        """Fail fast if no valid EUMETSAT credentials."""
        user = os.environ.get("EUMETSAT_USER")
        token = os.environ.get("EUMETSAT_TOKEN")

        # Treat None, empty string, or all-whitespace as missing
        if not (user and user.strip()) and not (token and token.strip()):
            print(f"[adapter] {self.__class__.__name__} — skipping (no credentials)", file=sys.stderr)
            raise RuntimeError(
                "EUMETSAT credentials not provided — set EUMETSAT_USER/PASS or EUMETSAT_TOKEN in .env"
            )


    def search(self, params: SearchParams) -> Iterable[Item]:
        self._check_credentials()

        headers = {}
        token = self.token_mgr.get()
        if token and not token.startswith("fake-token"):
            headers["Authorization"] = f"Bearer {token}"

        q = {
            "collectionId": params.collections[0] if params.collections else "sentinel-3-olci",
            "startDate": params.time.split("/")[0] if params.time else None,
            "endDate": params.time.split("/")[1] if params.time and "/" in params.time else None,
            "limit": params.limit or 10,
        }
        q = {k: v for k, v in q.items() if v}

        r = self.http.get(f"{CODA_API}/search", params=q, headers=headers, auth=self._basic_auth_if_needed(token))
        r.raise_for_status()
        data = r.json()

        for feature in data.get("features", []):
            yield map_coda_item(feature)

    def _basic_auth_if_needed(self, token: Optional[str]):
        if token and not token.startswith("fake-token"):
            return None
        user, pwd = os.getenv("EUMETSAT_USER"), os.getenv("EUMETSAT_PASS")
        return (user, pwd) if user and pwd else None

    def download(
        self,
        item: Item,
        asset_keys: Optional[List[str]] = None,
        prefer_jp2: bool = False,
        prefer_cog: bool = False
    ) -> Dict[str, Asset]:
        self._check_credentials()

        assets_to_get = asset_keys or list(item.assets.keys())
        out: Dict[str, Asset] = {}

        for key in assets_to_get:
            href = item.assets[key].href
            dest_key = f"{item.collection}/{item.id}/{os.path.basename(href)}"

            headers = {}
            token = self.token_mgr.get()
            if token and not token.startswith("fake-token"):
                headers["Authorization"] = f"Bearer {token}"

            tmp_path = Path("/tmp") / os.path.basename(href)
            with self.http.stream("GET", href, headers=headers, auth=self._basic_auth_if_needed(token)) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            local_path = self.sink.put(str(tmp_path), dest_key)
            out[key] = Asset(**{**item.assets[key].__dict__, "local_path": local_path})

        return out

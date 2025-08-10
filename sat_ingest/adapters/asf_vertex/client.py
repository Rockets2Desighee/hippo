# # sat_ingest/adapters/asf_vertex/client.py
# from __future__ import annotations
# from typing import Iterable, Optional, Sequence, Dict
# import sys

# # Core types/protocols already used across adapters
# from sat_ingest.core.base import CatalogAdapter
# from sat_ingest.core.search import SearchParams
# # from sat_ingest.core.models import Item, Asset # Uncomment when Item/Asset are defined

# class AsfVertexAdapter:  # implements CatalogAdapter protocol
#     """
#     Placeholder adapter for ASF Vertex.
#     - search(): prints params and yields nothing for now
#     - item(): prints id and returns None
#     - download(): prints and returns empty dict
#     """
#     name = "ASF Vertex"

#     def __init__(self, data_root: str | None = None, api_key: str | None = None, **_: dict):
#         self.data_root = data_root or "./data"
#         self.api_key = api_key  # You can also read from env later
#         print(f"[asf_vertex] init data_root={self.data_root} api_key={'***' if api_key else '(none)'}", file=sys.stderr)

#     # ---- query/search -------------------------------------------------------
#     def search(self, params: SearchParams) -> Iterable:
#         """
#         Placeholder: just print the normalized STAC-ish payload.
#         Later: call ASF Search (CMR/Vertex API), convert results -> Item objects, and yield progressively.
#         """
#         print(f"[asf_vertex] search params={params.to_stac_payload()}", file=sys.stderr)
#         # yield from []  # nothing for now
#         return []
#         # When implemented:
#         # for feat in self._page_results(params):
#         #     yield self._to_item(feat)

#     # ---- single item fetch (optional) ---------------------------------------
#     def item(self, item_id: str) -> Optional:
#         print(f"[asf_vertex] item({item_id})", file=sys.stderr)
#         return None

#     # ---- download -----------------------------------------------------------
#     def download(
#         self,
#         item,  # when wired up, type: Item
#         asset_keys: Optional[Sequence[str]] = None,
#         prefer_jp2: bool = False,
#         prefer_cog: bool = False,
#         **kwargs,
#     ) -> Dict[str, dict]:  # later: Dict[str, Asset]
#         """
#         Placeholder: print intent and return empty mapping.
#         Later: choose URLs for requested assets, stream to disk under data_root, return updated Asset objects.
#         """
#         print(f"[asf_vertex] download item={getattr(item, 'id', '(unknown)')} "
#               f"asset_keys={asset_keys} prefer_jp2={prefer_jp2} prefer_cog={prefer_cog}", file=sys.stderr)
#         return {}


from __future__ import annotations
import sys
from typing import Iterable, Optional, Sequence, Dict

from sat_ingest.core.search import SearchParams
# If/when you return real Items/Assets, import your models:
# from sat_ingest.core.models import Item, Asset

class AsfVertexAdapter:
    name = "ASF Vertex"

    def __init__(self, data_root: str | None = None, **_):
        self.data_root = data_root or "./data"
        print(f"[asf_vertex] init data_root={self.data_root}", file=sys.stderr)

    def search(self, params: SearchParams) -> Iterable:
        print(f"[asf_vertex] search params={params.to_stac_payload()}", file=sys.stderr)
        return []  # placeholder: yield nothing for now

    def item(self, item_id: str) -> Optional:
        print(f"[asf_vertex] item({item_id})", file=sys.stderr)
        return None

    def download(
        self,
        item,
        asset_keys: Optional[Sequence[str]] = None,
        prefer_jp2: bool = False,
        prefer_cog: bool = False,
        **kwargs,
    ) -> Dict[str, dict]:
        print(f"[asf_vertex] download item={getattr(item, 'id', '(unknown)')} "
              f"asset_keys={asset_keys} prefer_jp2={prefer_jp2} prefer_cog={prefer_cog}",
              file=sys.stderr)
        return {}

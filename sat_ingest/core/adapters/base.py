from __future__ import annotations
from typing import Iterable, Protocol, Optional, Dict, Any, Sequence
from dataclasses import dataclass
from sat_ingest.core.models import Item, Asset
from sat_ingest.core.search import SearchParams

class CatalogAdapter(Protocol):
    """Minimal contract every source-specific adapter must satisfy."""

    name: str  # add the name, e.g., "Earth Search STAC"

    def search(self, params: SearchParams) -> Iterable[Item]:
        """Return a (possibly lazy) iterable of Items matching the search.
        Items should be yielded as they are fetched to enable streaming.
        """
        ...

    def item(self, item_id: str) -> Optional[Item]:
        """Fetch a single item by its id (if endpoint supports it)."""
        ...

    def download(self, item: Item, asset_keys: Optional[Sequence[str]] = None, **kwargs) -> Dict[str, Asset]:
        """Download selected assets of an item.
        Returns a mapping of "asset key" to "Asset with updated local path".
        """
        ...
        
        
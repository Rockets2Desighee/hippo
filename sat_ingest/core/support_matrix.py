# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Optional, Tuple

# @dataclass
# class SourceChoice:
#     adapter: str  # registry key, e.g. "stac_generic", "noaa_goes"
#     reason: str

# _DEFAULT = {
#     ("sentinel-2", "L2A"): SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),
#     ("landsat-8", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),
#     ("landsat-9", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),
#     ("goes-16", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("goes-17", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("goes-18", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("nexrad", None):     SourceChoice(adapter="noaa_nexrad", reason="NOAA Open Data on AWS"),
# }

# class SupportMatrix:
#     def __init__(self, overrides: dict | None = None):
#         self._rules = {**_DEFAULT, **(overrides or {})}

#     def resolve(self, satellite: str, product: Optional[str]) -> SourceChoice:
#         key_exact: Tuple[str, Optional[str]] = (satellite.lower(), product.upper() if product else None)
#         key_fallback: Tuple[str, Optional[str]] = (satellite.lower(), None)

#         if key_exact in self._rules:
#             return self._rules[key_exact]
#         if key_fallback in self._rules:
#             return self._rules[key_fallback]
#         # last resort: STAC generic
#         return SourceChoice(adapter="stac_generic", reason="Fallback to STAC where available")

# sat_ingest/core/support_matrix.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class SourceChoice:
    adapter: str  # registry key, e.g. "stac_generic", "noaa_goes"
    reason: str
    collections: Optional[Tuple[str, ...]] = None  # default STAC collections (if adapter == stac_generic)

# Keep the matrix conservative; add collections where we're confident.
_DEFAULT = {
    # Sentinel-2 L2A → Earth Search STAC collection
    ("sentinel-2", "L2A"): SourceChoice(
        adapter="stac_generic",
        reason="Earth Search STAC",
        collections=("sentinel-2-l2a",),
    ),

    # Landsat examples (leave collections None if you're not 100% sure of the collection id)
    ("landsat-8", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),
    ("landsat-9", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),

    # NOAA families (no collections because these won’t use STAC generic once the adapter exists)
    ("goes-16", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
    ("goes-17", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
    ("goes-18", None):    SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
    ("nexrad", None):     SourceChoice(adapter="noaa_nexrad", reason="NOAA Open Data on AWS"),
}



class SupportMatrix:
    def __init__(self, overrides: dict | None = None):
        self._rules = {**_DEFAULT, **(overrides or {})}

    def resolve(self, satellite: str, product: Optional[str]) -> SourceChoice:
        key_exact: Tuple[str, Optional[str]] = (satellite.lower(), product.upper() if product else None)
        key_fallback: Tuple[str, Optional[str]] = (satellite.lower(), None)

        if key_exact in self._rules:
            return self._rules[key_exact]
        if key_fallback in self._rules:
            return self._rules[key_fallback]
        # last resort: STAC generic with no pinned collections
        return SourceChoice(adapter="stac_generic", reason="Fallback to STAC where available")

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


#####################################
# WORKS AS OF AUGUST 10: 1:31 AM
#####################################


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






#####################################
# support S1, S2, S3, S5P, Landsat, and GOES in the same fallback system
#####################################

# from __future__ import annotations
# from dataclasses import dataclass
# from typing import List, Optional

# @dataclass
# class SupportChoice:
#     adapter: str
#     reason: str
#     collections: Optional[List[str]] = None

# class SupportMatrix:
#     """
#     Maps (satellite, product) -> default adapter + collections.
#     Used for automatic adapter selection and fallback ordering.
#     """

#     def __init__(self):
#         # Define support for multiple satellites and products
#         self._matrix = {
#             # Sentinel-1
#             ("sentinel-1", "GRD"): SupportChoice(
#                 adapter="stac_generic",
#                 reason="resolved via Support Matrix",
#                 collections=["sentinel-1-grd"]
#             ),
#             # Sentinel-2
#             ("sentinel-2", "L2A"): SupportChoice(
#                 adapter="cdse_stac",
#                 reason="resolved via Support Matrix",
#                 collections=["sentinel-2-l2a"]
#             ),
#             # Sentinel-3
#             ("sentinel-3", "OLCI"): SupportChoice(
#                 adapter="cdse_stac",
#                 reason="resolved via Support Matrix",
#                 collections=["sentinel-3-olci"]
#             ),
#             # Sentinel-5P
#             ("sentinel-5p", "L2"): SupportChoice(
#                 adapter="cdse_stac",
#                 reason="resolved via Support Matrix",
#                 collections=["sentinel-5p-l2"]
#             ),
#             # Landsat
#             ("landsat-8", "L2"): SupportChoice(
#                 adapter="stac_generic",
#                 reason="resolved via Support Matrix",
#                 collections=["landsat-8-l2"]
#             ),
#             ("landsat-9", "L2"): SupportChoice(
#                 adapter="stac_generic",
#                 reason="resolved via Support Matrix",
#                 collections=["landsat-9-l2"]
#             ),
#             # NOAA GOES
#             ("noaa-goes", "ABI-L1b-Rad"): SupportChoice(
#                 adapter="noaa_goes",
#                 reason="resolved via Support Matrix",
#                 collections=["goes-16-abi-l1b-rad"]
#             ),
#         }

#     def resolve(self, satellite: str, product: Optional[str] = None) -> SupportChoice:
#         key = (satellite.lower(), product)
#         if key in self._matrix:
#             return self._matrix[key]
#         raise ValueError(f"No support entry for satellite={satellite}, product={product}")

#     def get_fallbacks(self, satellite: str, product: Optional[str] = None) -> List[str]:
#         """
#         Return a default fallback order for this satellite/product.
#         """
#         primary = self.resolve(satellite, product).adapter
#         # Simplified: if not NOAA, try cdse_stac then stac_generic
#         if primary == "noaa_goes":
#             return ["noaa_goes", "stac_generic"]
#         return ["cdse_stac", "stac_generic"]

#####################################
#####################################






#####################################
# THIS ONE WORKS FOR ALL SATELLITE AND
# ADAPTERS WITH PLACEHOLDERS
#####################################

# # sat_ingest/core/support_matrix.py
# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Optional, Tuple

# @dataclass
# class SourceChoice:
#     adapter: str
#     reason: str
#     collections: Optional[Tuple[str, ...]] = None

# _DEFAULT = {
#     # Sentinel
#     ("sentinel-1", None): SourceChoice(adapter="stac_generic", reason="Earth Search STAC", collections=("sentinel-1-grd",)),
#     ("sentinel-2", "L2A"): SourceChoice(adapter="stac_generic", reason="Earth Search STAC", collections=("sentinel-2-l2a",)),
#     ("sentinel-3", None): SourceChoice(adapter="stac_generic", reason="STAC Placeholder"),
#     ("sentinel-5p", None): SourceChoice(adapter="stac_generic", reason="STAC Placeholder"),

#     # Landsat
#     ("landsat-8", "L2"): SourceChoice(adapter="stac_generic", reason="Earth Search STAC", collections=("landsat-c2-l2",)),
#     ("landsat-9", "L2"): SourceChoice(adapter="stac_generic", reason="Earth Search STAC", collections=("landsat-c2-l2",)),

#     # NOAA GOES/NEXRAD
#     ("goes-16", None): SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("goes-17", None): SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("goes-18", None): SourceChoice(adapter="noaa_goes", reason="NOAA Open Data on AWS"),
#     ("nexrad", None): SourceChoice(adapter="noaa_nexrad", reason="NOAA Open Data on AWS"),

#     # NASA DAACs
#     ("modis", None): SourceChoice(adapter="daac_laads", reason="NASA LAADS DAAC"),
#     ("viirs", None): SourceChoice(adapter="daac_laads", reason="NASA LAADS DAAC"),
#     ("podaac", None): SourceChoice(adapter="daac_podaac", reason="NASA PO.DAAC"),
#     ("nsidc", None): SourceChoice(adapter="daac_nsidc", reason="NASA NSIDC"),

#     # AWS Public datasets
#     ("aws_s3", None): SourceChoice(adapter="aws_s3", reason="AWS Public Dataset"),

#     # Google Earth Engine
#     ("gee", None): SourceChoice(adapter="gee", reason="Google Earth Engine"),

#     # EUMETSAT
#     ("eumetsat", None): SourceChoice(adapter="eumetsat", reason="EUMETSAT Data Store"),

#     # Copernicus CDSE
#     ("cdse", None): SourceChoice(adapter="cdse_stac", reason="Copernicus Data Space Ecosystem"),
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
#         return SourceChoice(adapter="stac_generic", reason="Fallback to STAC where available")

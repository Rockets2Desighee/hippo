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


# # sat_ingest/core/support_matrix.py
# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Optional, Tuple

# @dataclass
# class SourceChoice:
#     adapter: str  # registry key, e.g. "stac_generic", "noaa_goes"
#     reason: str
#     collections: Optional[Tuple[str, ...]] = None  # default STAC collections (if adapter == stac_generic)
#     all_adapters: Optional[list[str]] = None # to support multiple adapters for the same satellite/product

# # Keep the matrix conservative; add collections where we're confident.

# # This matches how your SupportMatrix chooses an adapter per (satellite, product) and stores an explanation - and optionally STAC collections-used elsewhere in the CLI .
# _DEFAULT = {
#     # Sentinel-2 L2A → Earth Search STAC collection
#     ("sentinel-2", "L2A"): SourceChoice(
#         adapter="stac_generic",
#         reason="Earth Search STAC",
#         collections=("sentinel-2-l2a",),
#         all_adapters=["stac_generic", "cdse_stac"]
#     ),
#     # Sentinel-1 GRD from ASF Vertex
#     ("sentinel-1","GRD"): SourceChoice(adapter="asf_vertex", reason="ASF Vertex (SAR)", 
#                                      collections=None, #(not STAC generic)
#                                      all_adapters=[ "asf_vertex", "cdse_stac", "stac_generic"]

#     ),

#     # Landsat examples (leave collections None if not 100% sure of the collection id)
#     ("landsat-8", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),
#     ("landsat-9", "L2"):  SourceChoice(adapter="stac_generic", reason="Earth Search STAC"),

#     # NOAA families (no collections because these won’t use STAC generic once the adapter exists)
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
#         # last resort: STAC generic with no pinned collections
#         return SourceChoice(adapter="stac_generic", reason="Fallback to STAC where available")
    
#     def get_fallbacks(self, satellite: str, product: Optional[str] = None) -> list[str]:
#         choice = self.resolve(satellite, product)
#         if choice.all_adapters:
#             return choice.all_adapters
#         # default: return primary adapter + stac_generic
#         return [choice.adapter, "stac_generic"]
    
#     def get_all_adapters(self, satellite: str, product: Optional[str] = None) -> list[str]:
#         """
#         Return all adapter names that declare support for this satellite/product.
#         """
#         sat = satellite.lower()
#         prod = product.upper() if product else None
#         matches = []
#         for (s, p), choice in self._rules.items():
#             if s == sat and (p == prod or p is None):
#                 if choice.adapter not in matches:
#                     matches.append(choice.adapter)
#         # Always end with stac_generic if not already present
#         if "stac_generic" not in matches:
#             matches.append("stac_generic")
#         return matches



################################
# one final try:
# support_matrix.py

# sat_ingest/support_matrix.py
from typing import Dict, List, Tuple

# (satellite, product) -> (primary_adapter, collections)
SATELLITE_PRODUCTS: Dict[Tuple[str, str], Tuple[str, List[str]]] = {
    # Optical Imaging
    ("sentinel-2", "L1C"): ("cdse_stac", ["sentinel-2-l1c"]),
    ("sentinel-2", "L2A"): ("cdse_stac", ["sentinel-2-l2a"]),
    ("sentinel-3", "OLCI"): ("eumetsat_coda", ["sentinel-3-olci"]),
    ("sentinel-3", "SLSTR"): ("eumetsat_coda", ["sentinel-3-slstr"]),
    ("sentinel-3", "SRAL"): ("eumetsat_coda", ["sentinel-3-sral"]),
    ("landsat-8", "L1"): ("usgs_ee", ["landsat-8-l1"]),
    ("landsat-8", "L2"): ("usgs_ee", ["landsat-8-l2"]),
    ("landsat-9", "L1"): ("usgs_ee", ["landsat-9-l1"]),
    ("landsat-9", "L2"): ("usgs_ee", ["landsat-9-l2"]),
    ("landsat-7", "historical"): ("usgs_ee", ["landsat-7"]),
    ("landsat-5", "historical"): ("usgs_ee", ["landsat-5"]),
    ("planet-nicfi", "monthly-basemaps"): ("planet_api", []),
    ("cbers-4", "WFI"): ("aws_open_data", []),
    ("cbers-4", "MUX"): ("aws_open_data", []),
    ("spot", "various"): ("airbus_api", []),

    # Hyperspectral
    ("prisma", "hyperspectral"): ("asi_hub", []),
    ("enmap", "hyperspectral"): ("dlr_hub", []),
    ("desis", "hyperspectral"): ("teledyne_si", []),

    # Radar
    ("sentinel-1", "GRD"): ("cdse_stac", ["sentinel-1-grd"]),
    ("sentinel-1", "SLC"): ("cdse_stac", ["sentinel-1-slc"]),
    ("radarsat-2", "fine"): ("canadian_gov_api", []),
    ("alos-palsar", "L1.1"): ("jaxa", []),
    ("alos-palsar", "L1.5"): ("jaxa", []),
    ("terrasar-x", "spotlight"): ("airbus_api", []),
    ("iceye", "various"): ("iceye", []),

    # Thermal & Atmospheric
    ("modis-terra", "MOD"): ("laads_daac", []),
    ("modis-aqua", "MYD"): ("laads_daac", []),
    ("viirs-suomi-npp", "VNP"): ("laads_daac", []),
    ("viirs-noaa-20", "VJ"): ("laads_daac", []),
    ("ecostress", "LST"): ("lp_daac", []),
    ("snpp", "VIIRS"): ("noaa_class", []),

    # Weather & Geostationary
    ("goes-16", "ABI-L1b"): ("noaa_goes", []),
    ("goes-17", "ABI-L1b"): ("noaa_goes", []),
    ("goes-18", "ABI-L1b"): ("noaa_goes", []),
    ("himawari-8", "AHI"): ("jma_himawaricast", []),
    ("himawari-9", "AHI"): ("jma_himawaricast", []),
    ("meteosat", "SEVIRI"): ("eumetsat_coda", []),

    # Atmospheric Composition
    ("sentinel-5p", "L2"): ("cdse_stac", []),
    ("omi-aura", "OML2"): ("nasa_ges_disc", []),
    ("tropomi", "L2"): ("cdse_stac", []),

    # Cryosphere
    ("icesat-2", "ATL"): ("nsidc_daac", []),
    ("cryosat-2", "ice-thickness"): ("esa", []),

    # Oceanography
    ("jason-3", "altimetry"): ("podaac", []),
    ("sentinel-6", "altimetry"): ("podaac", []),
    ("smap", "soil-moisture"): ("nsidc", []),
    ("swot", "surface-water"): ("podaac", []),
}

# Adapter support mapping
ADAPTER_SUPPORT: Dict[str, List[Tuple[str, str]]] = {}
for (sat, prod), (primary, _) in SATELLITE_PRODUCTS.items():
    ADAPTER_SUPPORT.setdefault(primary, []).append((sat, prod))
# Add generic adapters
for adapter in ["stac_generic", "gee", "aws_open_data"]:
    ADAPTER_SUPPORT[adapter] = list(SATELLITE_PRODUCTS.keys())

def get_primary(satellite: str, product: str):
    return SATELLITE_PRODUCTS.get((satellite, product))

def get_all_adapters(satellite: str, product: str) -> List[str]:
    adapters = []
    for adapter, pairs in ADAPTER_SUPPORT.items():
        if (satellite, product) in pairs and adapter not in adapters:
            adapters.append(adapter)
    return adapters





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

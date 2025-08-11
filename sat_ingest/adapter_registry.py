# from __future__ import annotations
# from typing import Any

# # Required adapter
# from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
# from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter 

# # Optional adapters (may not exist yet); keep try/except so imports don’t break Milestone 1
# try:
#     from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter  # noqa: F401
# except Exception:
#     NoaaGoesAdapter = None  # type: ignore

# REGISTRY = {
#     "stac_generic": StacGenericAdapter,
#     "noaa_goes": NoaaGoesAdapter,  # may be None until implemented
     
# }

# def build_adapter(name: str, **kwargs: Any):
#     cls = REGISTRY.get(name)
#     if cls is None:
#         raise ValueError(f"Adapter '{name}' is not available/implemented.")
#     return cls(**kwargs)



#####################################
# support S1, S2, S3, S5P, Landsat, and GOES in the same fallback system
#####################################

# from __future__ import annotations
# from typing import Any

# from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
# try:
#     from sat_ingest.adapters.cdse_stac.client import CdseStacAdapter
# except ImportError:
#     CdseStacAdapter = None

# try:
#     from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter
# except ImportError:
#     NoaaGoesAdapter = None

# REGISTRY = {
#     "stac_generic": StacGenericAdapter,
#     "cdse_stac": CdseStacAdapter,
#     "noaa_goes": NoaaGoesAdapter,
# }

# def build_adapter(name: str, **kwargs: Any):
#     cls = REGISTRY.get(name)
#     if cls is None:
#         raise ValueError(f"Adapter '{name}' is not available/implemented.")
#     return cls(**kwargs)




##########################
# 10 august 2:31 PM
##########################

# # sat_ingest/adapter_registry.py
# from __future__ import annotations

# from typing import Any

# # Core / always-present
# from sat_ingest.adapters.stac_generic.client import StacGenericAdapter

# # Optional adapters — keep imports resilient so missing ones don’t crash CLI
# try:
#     from sat_ingest.adapters.cdse_stac.client import CdseStacAdapter
# except Exception:  # noqa: BLE001 - be liberal here to keep registry resilient
#     CdseStacAdapter = None

# try:
#     from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter
# except Exception:
#     NoaaGoesAdapter = None

# try:
#     # relies on sat_ingest/adapters/asf_vertex/__init__.py exposing AsfVertexAdapter
#     from sat_ingest.adapters.asf_vertex import AsfVertexAdapter
# except Exception:
#     AsfVertexAdapter = None  # keep registry resilient

# REGISTRY = {
#     "stac_generic": StacGenericAdapter,
#     "cdse_stac": CdseStacAdapter,
#     "noaa_goes": NoaaGoesAdapter,
#     "asf_vertex": AsfVertexAdapter,  # may be None if not implemented
# }

# def build_adapter(name: str, **kwargs: Any):
#     """
#     Construct an adapter by name. Raises a friendly error if the adapter
#     is not registered or is registered as None (i.e., optional import failed).
#     """
#     cls = REGISTRY.get(name)
#     if cls is None:
#         available = ", ".join(sorted(k for k, v in REGISTRY.items() if v is not None))
#         raise ValueError(
#             f"Adapter '{name}' is not available/implemented. "
#             f"Available: {available or '(none)'}"
#         )
#     return cls(**kwargs)



################################### #####################################################
# ONE FINAL TRY

# sat_ingest/adapter_registry.py
from typing import Any
from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
try:
    from sat_ingest.adapters.cdse_stac.client import CdseStacAdapter
except ImportError:
    CdseStacAdapter = None
try:
    from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter
except ImportError:
    NoaaGoesAdapter = None

# Placeholder imports
from sat_ingest.adapters.aws_open_data.client import AwsOpenDataAdapter
from sat_ingest.adapters.gee.client import GeeAdapter
from sat_ingest.adapters.eumetsat_coda.client import EumetsatCodaAdapter
from sat_ingest.adapters.usgs_ee.client import UsgsEarthExplorerAdapter
from sat_ingest.adapters.podaac.client import PodaacAdapter
from sat_ingest.adapters.nsidc.client import NsidcAdapter
from sat_ingest.adapters.laads_daac.client import LaadsDaacAdapter
from sat_ingest.adapters.inpe.client import InpeAdapter
from sat_ingest.adapters.planet_api.client import PlanetApiAdapter
from sat_ingest.adapters.airbus_api.client import AirbusApiAdapter
from sat_ingest.adapters.asi_hub.client import AsiHubAdapter
from sat_ingest.adapters.dlr_hub.client import DlrHubAdapter
from sat_ingest.adapters.teledyne_si.client import TeledyneSiAdapter
from sat_ingest.adapters.canadian_gov_api.client import CanadianGovApiAdapter
from sat_ingest.adapters.jaxa.client import JaxaAdapter
from sat_ingest.adapters.iceye.client import IceyeAdapter
from sat_ingest.adapters.noaa_class.client import NoaaClassAdapter
from sat_ingest.adapters.jma_himawaricast.client import JmaHimawaricastAdapter
from sat_ingest.adapters.s5p_hub.client import S5pHubAdapter
from sat_ingest.adapters.nasa_ges_disc.client import NasaGesDiscAdapter
from sat_ingest.adapters.nsidc_daac.client import NsidcDaacAdapter

REGISTRY = {
    "stac_generic": StacGenericAdapter,
    "cdse_stac": CdseStacAdapter,
    "noaa_goes": NoaaGoesAdapter,
    "aws_open_data": AwsOpenDataAdapter,
    "gee": GeeAdapter,
    "eumetsat_coda": EumetsatCodaAdapter,
    "usgs_ee": UsgsEarthExplorerAdapter,
    "podaac": PodaacAdapter,
    "nsidc": NsidcAdapter,
    "laads_daac": LaadsDaacAdapter,
    "inpe": InpeAdapter,
    "planet_api": PlanetApiAdapter,
    "airbus_api": AirbusApiAdapter,
    "asi_hub": AsiHubAdapter,
    "dlr_hub": DlrHubAdapter,
    "teledyne_si": TeledyneSiAdapter,
    "canadian_gov_api": CanadianGovApiAdapter,
    "jaxa": JaxaAdapter,
    "iceye": IceyeAdapter,
    "noaa_class": NoaaClassAdapter,
    "jma_himawaricast": JmaHimawaricastAdapter,
    "s5p_hub": S5pHubAdapter,
    "nasa_ges_disc": NasaGesDiscAdapter,
    "nsidc_daac": NsidcDaacAdapter,
}

def build_adapter(name: str, **kwargs: Any):
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Adapter '{name}' is not available.")
    return cls(**kwargs)




# #####################################################
# # THIS WORKS FOR ALL SATELLITES AND ADAPTERS
# WITH PLACEHOLDERS
# #####################################################

# from __future__ import annotations
# from typing import Any

# # Required adapters
# from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
# from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter

# # Placeholder adapter classes for not-yet-implemented sources
# class PlaceholderAdapter:
#     def __init__(self, **kwargs):
#         pass
#     def search(self, params): raise NotImplementedError("Search not implemented for this placeholder adapter.")
#     def download(self, item, **kwargs): raise NotImplementedError("Download not implemented for this placeholder adapter.")

# # Optional adapters (wrap in try/except in case they exist)
# try:
#     from sat_ingest.adapters.cdse_stac.client import CdseStacAdapter
# except ImportError:
#     CdseStacAdapter = PlaceholderAdapter

# REGISTRY = {
#     "stac_generic": StacGenericAdapter,
#     "noaa_goes": NoaaGoesAdapter,
#     "cdse_stac": CdseStacAdapter,

#     # Placeholder registry entries
#     "noaa_nexrad": PlaceholderAdapter,
#     "daac_laads": PlaceholderAdapter,
#     "daac_podaac": PlaceholderAdapter,
#     "daac_nsidc": PlaceholderAdapter,
#     "aws_s3": PlaceholderAdapter,
#     "gee": PlaceholderAdapter,
#     "eumetsat": PlaceholderAdapter,
# }

# def build_adapter(name: str, **kwargs: Any):
#     cls = REGISTRY.get(name)
#     if cls is None:
#         raise ValueError(f"Adapter '{name}' is not available/implemented.")
#     return cls(**kwargs)

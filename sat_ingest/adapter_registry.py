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
##########################

# from __future__ import annotations
# from typing import Any

# # Required adapters
# from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
# from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter

# # Optional adapters (may not exist yet)
# try:
#     from sat_ingest.adapters.cdse_stac.client import CdseStacAdapter  # noqa: F401
# except Exception:
#     CdseStacAdapter = None  # type: ignore

# REGISTRY = {
#     "stac_generic": StacGenericAdapter,
#     "noaa_goes": NoaaGoesAdapter,  # may be None until implemented
#     "cdse_stac": CdseStacAdapter,  # may be None if not implemented
# }

# def build_adapter(name: str, **kwargs: Any):
#     cls = REGISTRY.get(name)
#     if cls is None:
#         raise ValueError(f"Adapter '{name}' is not available/implemented.")
#     return cls(**kwargs)




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

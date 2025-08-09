from __future__ import annotations
from typing import Any

# Required adapter
from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter 

# Optional adapters (may not exist yet); keep try/except so imports don’t break Milestone 1
try:
    from sat_ingest.adapters.noaa_goes.client import NoaaGoesAdapter  # noqa: F401
except Exception:
    NoaaGoesAdapter = None  # type: ignore

REGISTRY = {
    "stac_generic": StacGenericAdapter,
    "noaa_goes": NoaaGoesAdapter,  # may be None until implemented
     
}

def build_adapter(name: str, **kwargs: Any):
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Adapter '{name}' is not available/implemented.")
    return cls(**kwargs)



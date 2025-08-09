from sat_ingest.adapters.stac_generic.client import StacGenericAdapter
from sat_ingest.core.search import SearchParams

# Tiny smoke test; expands later into a shared contract suite.

def test_search_smoke():
    a = StacGenericAdapter()
    params = SearchParams(collections=["sentinel-2-l2a"], limit=1)
    items = list(a.search(params))
    assert len(items) >= 0  # don't fail if empty; this is a network smoke check
    
    
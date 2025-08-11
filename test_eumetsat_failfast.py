# test_eumetsat_failfast.py
import sys
from sat_ingest.adapters.eumetsat_coda.client import EumetsatCodaAdapter
from sat_ingest.core.search import SearchParams

print("Running EumetsatCodaAdapter fail-fast test...\n")

try:
    adapter = EumetsatCodaAdapter()
    params = SearchParams(collections=["sentinel-3-olci"], limit=1)
    results = list(adapter.search(params))
    print(f"Search returned {len(results)} results")
except Exception as e:
    print(f"FAIL-FAST triggered: {e}", file=sys.stderr)

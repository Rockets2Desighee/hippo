# sat_ingest/adapters/eumetsat_coda/client.py
class EumetsatCodaAdapter:
    def __init__(self, **kwargs):
        print("[eumetsat_coda] init", kwargs)

    def search(self, params):
        print("[eumetsat_coda] search", params)
        return []

    def download(self, item, asset_keys):
        print("[eumetsat_coda] download", item, asset_keys)
        return True

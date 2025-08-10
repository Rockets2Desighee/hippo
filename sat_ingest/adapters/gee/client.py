# sat_ingest/adapters/gee/client.py
class GEEAdapter:
    def __init__(self, **kwargs):
        print("[gee] init", kwargs)

    def search(self, params):
        print("[gee] search", params)
        return []

    def download(self, item, asset_keys):
        print("[gee] download", item, asset_keys)
        return True

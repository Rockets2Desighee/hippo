# sat_ingest/adapters/planet_api/client.py
class PlanetApiAdapter:
    def __init__(self, **kwargs):
        print("[planet_api] init", kwargs)

    def search(self, params):
        print("[planet_api] search", params)
        return []

    def download(self, item, asset_keys):
        print("[planet_api] download", item, asset_keys)
        return True

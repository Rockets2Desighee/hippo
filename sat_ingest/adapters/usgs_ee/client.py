# sat_ingest/adapters/usgs_ee/client.py
class UsgsEarthExplorerAdapter:
    def __init__(self, **kwargs):
        print("[usgs_ee] init", kwargs)

    def search(self, params):
        print("[usgs_ee] search", params)
        return []

    def download(self, item, asset_keys):
        print("[usgs_ee] download", item, asset_keys)
        return True

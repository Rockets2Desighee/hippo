# sat_ingest/adapters/jma_himawaricast/client.py
class JmaHimawaricastAdapter:
    def __init__(self, **kwargs):
        print("[jma_himawaricast] init", kwargs)

    def search(self, params):
        print("[jma_himawaricast] search", params)
        return []

    def download(self, item, asset_keys):
        print("[jma_himawaricast] download", item, asset_keys)
        return True

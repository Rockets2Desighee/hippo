# sat_ingest/adapters/inpe/client.py
class InpeAdapter:
    def __init__(self, **kwargs):
        print("[inpe] init", kwargs)

    def search(self, params):
        print("[inpe] search", params)
        return []

    def download(self, item, asset_keys):
        print("[inpe] download", item, asset_keys)
        return True

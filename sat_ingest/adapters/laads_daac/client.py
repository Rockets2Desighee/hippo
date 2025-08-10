# sat_ingest/adapters/laads_daac/client.py
class LaadsDaacAdapter:
    def __init__(self, **kwargs):
        print("[laads_daac] init", kwargs)

    def search(self, params):
        print("[laads_daac] search", params)
        return []

    def download(self, item, asset_keys):
        print("[laads_daac] download", item, asset_keys)
        return True

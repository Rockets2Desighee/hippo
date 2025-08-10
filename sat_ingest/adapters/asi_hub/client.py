# sat_ingest/adapters/asi_hub/client.py
class AsiHubAdapter:
    def __init__(self, **kwargs):
        print("[asi_hub] init", kwargs)

    def search(self, params):
        print("[asi_hub] search", params)
        return []

    def download(self, item, asset_keys):
        print("[asi_hub] download", item, asset_keys)
        return True

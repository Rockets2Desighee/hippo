# sat_ingest/adapters/s5p_hub/client.py
class S5pHubAdapter:
    def __init__(self, **kwargs):
        print("[s5p_hub] init", kwargs)

    def search(self, params):
        print("[s5p_hub] search", params)
        return []

    def download(self, item, asset_keys):
        print("[s5p_hub] download", item, asset_keys)
        return True

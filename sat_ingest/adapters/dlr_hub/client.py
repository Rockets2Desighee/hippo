# sat_ingest/adapters/dlr_hub/client.py
class DlrHubAdapter:
    def __init__(self, **kwargs):
        print("[dlr_hub] init", kwargs)

    def search(self, params):
        print("[dlr_hub] search", params)
        return []

    def download(self, item, asset_keys):
        print("[dlr_hub] download", item, asset_keys)
        return True

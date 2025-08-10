# sat_ingest/adapters/airbus_api/client.py
class AirbusApiAdapter:
    def __init__(self, **kwargs):
        print("[airbus_api] init", kwargs)

    def search(self, params):
        print("[airbus_api] search", params)
        return []

    def download(self, item, asset_keys):
        print("[airbus_api] download", item, asset_keys)
        return True

# sat_ingest/adapters/iceye/client.py
class IceyeAdapter:
    def __init__(self, **kwargs):
        print("[iceye] init", kwargs)

    def search(self, params):
        print("[iceye] search", params)
        return []

    def download(self, item, asset_keys):
        print("[iceye] download", item, asset_keys)
        return True

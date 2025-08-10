# sat_ingest/adapters/noaa_class/client.py
class NoaaClassAdapter:
    def __init__(self, **kwargs):
        print("[noaa_class] init", kwargs)

    def search(self, params):
        print("[noaa_class] search", params)
        return []

    def download(self, item, asset_keys):
        print("[noaa_class] download", item, asset_keys)
        return True

# sat_ingest/adapters/podaac/client.py
class PodaacAdapter:
    def __init__(self, **kwargs):
        print("[podaac] init", kwargs)

    def search(self, params):
        print("[podaac] search", params)
        return []

    def download(self, item, asset_keys):
        print("[podaac] download", item, asset_keys)
        return True

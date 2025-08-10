# sat_ingest/adapters/jaxa/client.py
class JaxaAdapter:
    def __init__(self, **kwargs):
        print("[jaxa] init", kwargs)

    def search(self, params):
        print("[jaxa] search", params)
        return []

    def download(self, item, asset_keys):
        print("[jaxa] download", item, asset_keys)
        return True

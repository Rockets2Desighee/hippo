# sat_ingest/adapters/nsidc/client.py
class NsidcAdapter:
    def __init__(self, **kwargs):
        print("[nsidc] init", kwargs)

    def search(self, params):
        print("[nsidc] search", params)
        return []

    def download(self, item, asset_keys):
        print("[nsidc] download", item, asset_keys)
        return True

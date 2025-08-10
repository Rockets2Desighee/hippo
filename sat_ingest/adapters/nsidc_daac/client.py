# sat_ingest/adapters/nsidc_daac/client.py
class NsidcDaacAdapter:
    def __init__(self, **kwargs):
        print("[nsidc_daac] init", kwargs)

    def search(self, params):
        print("[nsidc_daac] search", params)
        return []

    def download(self, item, asset_keys):
        print("[nsidc_daac] download", item, asset_keys)
        return True

# sat_ingest/adapters/nasa_ges_disc/client.py
class NasaGesDiscAdapter:
    def __init__(self, **kwargs):
        print("[nasa_ges_disc] init", kwargs)

    def search(self, params):
        print("[nasa_ges_disc] search", params)
        return []

    def download(self, item, asset_keys):
        print("[nasa_ges_disc] download", item, asset_keys)
        return True

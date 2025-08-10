# sat_ingest/adapters/teledyne_si/client.py
class TeledyneSiAdapter:
    def __init__(self, **kwargs):
        print("[teledyne_si] init", kwargs)

    def search(self, params):
        print("[teledyne_si] search", params)
        return []

    def download(self, item, asset_keys):
        print("[teledyne_si] download", item, asset_keys)
        return True

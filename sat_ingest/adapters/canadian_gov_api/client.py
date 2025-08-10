# sat_ingest/adapters/canadian_gov_api/client.py
class CanadianGovApiAdapter:
    def __init__(self, **kwargs):
        print("[canadian_gov_api] init", kwargs)

    def search(self, params):
        print("[canadian_gov_api] search", params)
        return []

    def download(self, item, asset_keys):
        print("[canadian_gov_api] download", item, asset_keys)
        return True

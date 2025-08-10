# sat_ingest/adapters/aws_open_data/client.py
class AwsOpenDataAdapter:
    def __init__(self, **kwargs):
        print("[aws_open_data] init", kwargs)

    def search(self, params):
        print("[aws_open_data] search", params)
        return []

    def download(self, item, asset_keys):
        print("[aws_open_data] download", item, asset_keys)
        return True

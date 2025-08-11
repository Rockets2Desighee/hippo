# sat_ingest/adapters/cdse_stac/token.py
import os
import time
import requests

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

class TokenProvider:
    def __init__(self):
        self._cached_token = None
        self._expires_at = 0

    def _fetch_token(self, client_id: str, client_secret: str) -> str:
        """
        Request a new access token from CDSE using the client_credentials flow.
        We omit 'scope' entirely because some accounts do not allow 'stac' or other scopes.
        """
        resp = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=30
        )

        # If the request failed, raise with full response text for debugging
        if resp.status_code != 200:
            raise RuntimeError(f"Token request failed: {resp.status_code} {resp.text}")

        data = resp.json()
        self._cached_token = data.get("access_token")
        self._expires_at = time.time() + int(data.get("expires_in", 3600))
        return self._cached_token

    def get_access_token(self) -> str:
        """
        Get a valid CDSE access token.
        Always uses CLIENT_ID/CLIENT_SECRET; falls back to static ACCESS_TOKEN if set.
        """
        # Static token fallback (discouraged — expires quickly)
        token = os.getenv("CDSE_ACCESS_TOKEN")
        if token:
            return token

        client_id = os.getenv("CDSE_CLIENT_ID")
        client_secret = os.getenv("CDSE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise RuntimeError(
                "No CDSE credentials found. Set CDSE_CLIENT_ID and CDSE_CLIENT_SECRET in your environment."
            )

        # Refresh if missing or near expiry
        if not self._cached_token or time.time() >= self._expires_at - 60:
            return self._fetch_token(client_id, client_secret)

        return self._cached_token

# sat_ingest/adapters/cdse_stac/token.py
from __future__ import annotations
import os, time
import httpx

# Defaults are overridable in .env or env.example
CDSE_AUTH_URL    = os.environ.get("CDSE_AUTH_URL", "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token")
CDSE_CLIENT_ID   = os.environ.get("CDSE_CLIENT_ID")
CDSE_CLIENT_SEC  = os.environ.get("CDSE_CLIENT_SECRET")
CDSE_ACCESS_TOKEN_ENV = os.environ.get("CDSE_ACCESS_TOKEN")  # optional pre-fetched token

class TokenProvider:
    def __init__(self):
        self._tok = None
        self._exp = 0.0

    def _needs_refresh(self) -> bool:
        return not self._tok or (time.time() > (self._exp - 60))  # refresh 60s early

    def _fetch(self) -> tuple[str, float]:
        if CDSE_ACCESS_TOKEN_ENV:
            # If user provides a token, just use it (assume short-lived).
            return CDSE_ACCESS_TOKEN_ENV, time.time() + 3600

        if not (CDSE_CLIENT_ID and CDSE_CLIENT_SEC):
            raise RuntimeError(
                "CDSE token required. Set CDSE_ACCESS_TOKEN or CDSE_CLIENT_ID/CDSE_CLIENT_SECRET."
            )

        with httpx.Client(timeout=30.0) as c:
            r = c.post(
                CDSE_AUTH_URL,
                data={"grant_type": "client_credentials"},
                auth=(CDSE_CLIENT_ID, CDSE_CLIENT_SEC),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            r.raise_for_status()
            js = r.json()
            return js["access_token"], float(js.get("expires_in", 3600))

    def get_access_token(self) -> str:
        if self._needs_refresh():
            tok, ttl = self._fetch()
            self._tok = tok
            self._exp = time.time() + ttl
        return self._tok

# sat_ingest/adapters/eumetsat_coda/token.py
"""
Auth helper for EUMETSAT CODA (future use).

Planned behavior once real API is enabled:
- If EUMETSAT_TOKEN is set, use it.
- Else, exchange EUMETSAT_USER / EUMETSAT_PASS for an access token via CODA OAuth.
- Cache token in-memory with expiry; refresh when needed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os
import time

@dataclass
class CodaToken:
    access_token: str
    expires_at: float  # unix epoch seconds

    def is_expired(self) -> bool:
        # refresh slightly early
        return time.time() > (self.expires_at - 60)

class TokenManager:
    def __init__(self):
        self._cached: Optional[CodaToken] = None

    def get(self) -> Optional[str]:
        # 1) Use pre-provided token if present
        tok = os.getenv("EUMETSAT_TOKEN")
        if tok:
            return tok

        # 2) Placeholder: if username/password are present, pretend we fetched a token
        user = os.getenv("EUMETSAT_USER")
        pwd = os.getenv("EUMETSAT_PASS")
        if user and pwd:
            # Fake a token for now
            return f"fake-token-for:{user}"

        # 3) No token available
        return None

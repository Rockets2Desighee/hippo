from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class ApiKeyAuth:
    header: str
    value: str
    def headers(self) -> dict:
        return {self.header: self.value}

# Placeholders for future schemes (OAuth2, AWS SigV4)
@dataclass
class AwsConfig:
    # Either use a profile OR access keys (or neither, to fall back on default chain)
    profile: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    region: Optional[str] = None
    requester_pays: bool = True  # Landsat C2/L2 needs this

    @classmethod
    def from_env(cls) -> "AwsConfig":
        return cls(
            profile=os.getenv("AWS_PROFILE") or None,
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
            session_token=os.getenv("AWS_SESSION_TOKEN") or None,
            region=os.getenv("AWS_DEFAULT_REGION") or None,
            requester_pays=(os.getenv("AWS_REQUEST_PAYER", "requester").lower() == "requester"),
        )
    
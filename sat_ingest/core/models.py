from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass
class Asset:
    key: str
    href: str  # remote URL
    media_type: Optional[str] = None
    checksum: Optional[str] = None
    roles: tuple[str, ...] = ()
    local_path: Optional[str] = None  # will be filled after download

@dataclass
class Item:
    id: str
    collection: Optional[str]
    datetime: Optional[str]
    bbox: Optional[list[float]]
    geometry: Optional[dict]
    properties: Dict[str, Any] = field(default_factory=dict)
    assets: Dict[str, Asset] = field(default_factory=dict)
    
    
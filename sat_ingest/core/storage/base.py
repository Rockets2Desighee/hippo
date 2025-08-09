from __future__ import annotations
from abc import ABC, abstractmethod

class StorageSink(ABC):
    @abstractmethod
    def put(self, src_path: str, dest_key: str) -> str:
        """Store a local file and return a URL or path."""
        ...
        
        
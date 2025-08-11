# sat_ingest/adapters/planet_api/client.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional
import os, json, time

try:
    from PIL import Image
    import numpy as np
except Exception:
    Image = None
    np = None

@dataclass
class SearchResult:
    id: str
    collection: str
    datetime: str

@dataclass
class DownloadedAsset:
    key: str
    local_path: str

class PlanetApiAdapter:
    def __init__(self, **kwargs: Any):
        # os.environ.get("PL_API_KEY")
        self.data_root = Path(kwargs.get("data_root") or os.environ.get("SAT_DATA_ROOT", "./data")).resolve()
        self.data_root.mkdir(parents=True, exist_ok=True)

    def search(self, params) -> Iterable[SearchResult]:
        collections = params.collections or ["planet-nicfi-monthly-basemaps"]
        tstamp = int(time.time())
        return [SearchResult(id=f"{c}-{tstamp}-0", collection=c, datetime=str(params.time or "1970-01-01"))]

    def _write_gray_png(self, path: Path, size=(64, 64)):
        if Image is None or np is None:
            path.write_bytes(b"PNG PLACEHOLDER")
            return
        import numpy as np
        arr = (np.linspace(0, 255, size[0]*size[1]).reshape(size).astype("uint8"))
        Image.fromarray(arr, mode="L").save(path)

    def download(self, item: SearchResult, asset_keys: Optional[List[str]] = None,
                 prefer_jp2: bool = False, prefer_cog: bool = False) -> Dict[str, DownloadedAsset]:
        out_dir = self.data_root / item.collection / item.id
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "item.json").write_text(json.dumps({"id": item.id, "collection": item.collection}))
        keys = asset_keys or ["red", "green", "blue"]
        result: Dict[str, DownloadedAsset] = {}
        for k in keys:
            f = out_dir / f"{k}.png"
            self._write_gray_png(f, size=(128, 128))
            result[k] = DownloadedAsset(key=k, local_path=str(f))
        return result

# sat_ingest/adapters/jma_himawaricast/client.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional
import os, json, time
try:
    from PIL import Image
    import numpy as np
except Exception:
    Image=None; np=None

@dataclass
class SearchResult: id:str; collection:str; datetime:str
@dataclass
class DownloadedAsset: key:str; local_path:str

class JmaHimawaricastAdapter:
    def __init__(self, **kwargs: Any):
        self.data_root=Path(kwargs.get("data_root") or os.environ.get("SAT_DATA_ROOT","./data")).resolve()
        self.data_root.mkdir(parents=True, exist_ok=True)

    def search(self, params)->Iterable[SearchResult]:
        colls=params.collections or ["himawari-8-ahi","himawari-9-ahi"]
        t=int(time.time())
        return [SearchResult(id=f"{c}-{t}-{i}", collection=c, datetime=str(params.time or "1970-01-01"))
                for i,c in enumerate(colls[:max(1, params.limit or 1)])]

    def _write_png(self, p:Path, size=(64,64)):
        if Image is None or np is None: p.write_bytes(b"PNG PLACEHOLDER"); return
        arr=(np.linspace(0,255,size[0]*size[1]).reshape(size).astype("uint8"))
        Image.fromarray(arr, "L").save(p)

    def download(self, item:SearchResult, asset_keys:Optional[List[str]]=None,
                 prefer_jp2:bool=False, prefer_cog:bool=False)->Dict[str,DownloadedAsset]:
        d=self.data_root/item.collection/item.id; d.mkdir(parents=True, exist_ok=True)
        (d/"item.json").write_text(json.dumps({"id":item.id,"collection":item.collection}))
        keys=asset_keys or ["red","green","blue"]
        out:Dict[str,DownloadedAsset]={}
        for k in keys:
            f=d/f"{k}.png"; self._write_png(f); out[k]=DownloadedAsset(k,str(f))
        return out

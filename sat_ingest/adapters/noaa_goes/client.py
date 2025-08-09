# from __future__ import annotations
# from typing import Iterable, Optional, Sequence, Dict
# from dataclasses import dataclass
# import datetime as dt
# import os
# import sys
# import tempfile
# import boto3
# from botocore.config import Config
# from botocore import UNSIGNED
# from botocore.exceptions import BotoCoreError, ClientError

# from sat_ingest.core.adapters.base import CatalogAdapter
# from sat_ingest.core.search import SearchParams
# from sat_ingest.core.models import Item, Asset
# from sat_ingest.core.storage.local import LocalSink
# from sat_ingest.core.http import HttpClient

# # NOAA GOES buckets commonly used:
# #   noaa-goes16, noaa-goes17, noaa-goes18
# # Object layout pattern (example for ABI L2 cloud products):
# #   abi/L2/CMIPF/{YYYY}/{DDD}/{HH}/OR_ABI-L2-CMIPF-M6C13_G16_sYYYYDDDHHMM....nc
# #
# # For scaffold:
# # - If --time is provided, we list a few keys under the derived prefix.
# # - If --time is missing OR listing fails, we emit one stub Item pointing to GOES_SAMPLE_URI
# #   so the CLI can run end-to-end immediately.

# DEFAULT_BUCKETS = {
#     "goes-16": "noaa-goes16",
#     "goes-17": "noaa-goes17",
#     "goes-18": "noaa-goes18",
# }

# # Allow overriding the demo object (handy for testing small files)
# _DEFAULT_SAMPLE_URI = os.environ.get("GOES_SAMPLE_URI", "s3://noaa-goes16/README.txt")


# @dataclass
# class GoesSearchConfig:
#     satellite: str = "goes-16"                 # goes-16/17/18
#     product_prefix: str = "ABI-L2-CMIPF"       # example product class
#     # You can extend this to cover channels, L1b vs L2, etc.


# class NoaaGoesAdapter(CatalogAdapter):
#     name = "NOAA GOES (AWS S3)"

#     def __init__(
#         self,
#         data_root: str | None = None,
#         satellite: str = "goes-16",
#         product_prefix: str = "ABI-L2-CMIPF",
#         sample_uri: str | None = None,
#     ):
#         self.sink = LocalSink(root=data_root)
#         self.satellite = satellite.lower()
#         self.product_prefix = product_prefix
#         self.bucket = DEFAULT_BUCKETS.get(self.satellite, "noaa-goes16")
#         # IMPORTANT: unsigned S3 client for AWS Open Data (no credentials required)
#         self.s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
#         # Downloads go through the unified client that supports s3://
#         self.http = HttpClient()
#         self.sample_uri = sample_uri or _DEFAULT_SAMPLE_URI

#     # -----------------------------
#     # Helpers
#     # -----------------------------
#     def _iter_s3_keys(self, prefix: str, max_keys: int) -> Iterable[str]:
#         paginator = self.s3.get_paginator("list_objects_v2")
#         count = 0
#         for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
#             for obj in page.get("Contents", []):
#                 yield obj["Key"]
#                 count += 1
#                 if count >= max_keys:
#                     return

#     def _parse_time_to_ydh(self, time_range: str):
#         """
#         Very simple ISO range parser -> (YYYY, DDD, HH) tuples to build prefixes.
#         Expects 'start/end', UTC. We’ll take the start hour only for scaffold.
#         """
#         start_s, _end_s = time_range.split("/")
#         start = dt.datetime.fromisoformat(start_s.replace("Z", ""))
#         yday = int(start.strftime("%j"))
#         return start.year, yday, start.hour

#     def _media_type_for_key(self, key: str) -> str:
#         return "application/netcdf" if key.lower().endswith(".nc") else "application/octet-stream"

#     def _yield_stub_item(self) -> Iterable[Item]:
#         item_id = f"{self.satellite}-stub"
#         assets = {
#             "sample": Asset(
#                 key="sample",
#                 href=self.sample_uri,
#                 media_type=self._media_type_for_key(self.sample_uri),
#             )
#         }
#         yield Item(
#             id=item_id,
#             collection=f"{self.satellite}-{self.product_prefix}".lower(),
#             datetime=None,
#             bbox=None,
#             geometry=None,
#             assets=assets,
#             properties={
#                 "note": "stub item from noaa_goes adapter; provide --time to list real S3 keys",
#                 "s3_bucket": self.bucket,
#             },
#         )

#     # -----------------------------
#     # Public API
#     # -----------------------------
#     def search(self, params: SearchParams) -> Iterable[Item]:
#         """
#         If time is given, list a handful of keys under a plausible ABI L2 CMIPF path (unsigned S3).
#         If not (or listing fails), return a single stub item that points at self.sample_uri.
#         """
#         if not params.time:
#             # No time: return stub
#             yield from self._yield_stub_item()
#             return

#         try:
#             year, yday, hour = self._parse_time_to_ydh(params.time)
#             # Example GOES path structure (simplified):
#             # abi/L2/CMIPF/YYYY/DDD/HH/
#             prefix = f"abi/L2/CMIPF/{year:04d}/{yday:03d}/{hour:02d}/"

#             limit = params.limit or 10
#             any_yielded = False
#             for key in self._iter_s3_keys(prefix, max_keys=limit):
#                 any_yielded = True
#                 item_id = os.path.basename(key)
#                 assets = {
#                     "data": Asset(
#                         key="data",
#                         href=f"s3://{self.bucket}/{key}",
#                         media_type=self._media_type_for_key(key),
#                     )
#                 }
#                 yield Item(
#                     id=item_id,
#                     collection=f"{self.satellite}-{self.product_prefix}".lower(),
#                     datetime=None,
#                     bbox=None,
#                     geometry=None,
#                     assets=assets,
#                     properties={"s3_bucket": self.bucket, "s3_key": key, "prefix": prefix},
#                 )

#             # If the prefix was empty (common if the hour has no files), offer a stub so CLI still works
#             if not any_yielded:
#                 yield from self._yield_stub_item()

#         except (ClientError, BotoCoreError, ValueError) as e:
#             # Most likely credentials/config or empty listing — fall back to stub for smooth UX
#             print(f"[noaa_goes] listing failed ({e.__class__.__name__}): {e}; returning stub item.", file=sys.stderr)
#             yield from self._yield_stub_item()

#     def item(self, item_id: str) -> Optional[Item]:
#         # Not trivial without an index; for scaffold we skip
#         return None

#     def download(self, item: Item, asset_keys: Optional[Sequence[str]] = None, **kwargs) -> Dict[str, Asset]:
#         """
#         Download selected assets.
#         Uses HttpClient.stream_download which supports s3:// (unsigned first, then creds if available).
#         If the object isn't available, writes a tiny placeholder file so the CLI still completes.
#         """
#         selected = asset_keys or list(item.assets.keys())
#         out: Dict[str, Asset] = {}

#         for k in selected:
#             if k not in item.assets:
#                 print(f"Warning: asset '{k}' not found on item {item.id}; skipping.", file=sys.stderr)
#                 continue

#             asset = item.assets[k]
#             href = asset.href
#             # Decide filename on disk: keep the asset key if no extension, else preserve basename
#             basename = os.path.basename(href) if href.startswith("s3://") else k
#             filename = basename if os.path.splitext(basename)[1] else k

#             with tempfile.NamedTemporaryFile(delete=False) as tmp:
#                 tmp_path = tmp.name

#             ok = True
#             try:
#                 self.http.stream_download(href, tmp_path, chunk_size=1024 * 512, on_chunk=None)
#             except Exception as e:
#                 ok = False
#                 # Graceful fallback: write a tiny placeholder so the pipeline doesn't break.
#                 try:
#                     with open(tmp_path, "wb") as f:
#                         f.write(
#                             (
#                                 "NOAA GOES adapter stub placeholder.\n"
#                                 f"Requested: {href}\n"
#                                 f"Reason: {e.__class__.__name__}: {e}\n"
#                             ).encode("utf-8")
#                         )
#                 except Exception:
#                     pass

#             dest_key = f"{item.collection}/{item.id}/{filename}"
#             dest_path = self.sink.put(tmp_path, dest_key)
#             asset.local_path = dest_path
#             out[k] = asset

#             try:
#                 os.remove(tmp_path)
#             except OSError:
#                 pass

#             if ok:
#                 print(f"Copied {href} -> {dest_path}")
#             else:
#                 print(f"Created placeholder for {href} -> {dest_path}", file=sys.stderr)

#         return out












from __future__ import annotations
from typing import Iterable, Optional, Sequence, Dict
from dataclasses import dataclass
import os
import sys
import tempfile
import boto3
from botocore.config import Config
from botocore import UNSIGNED
from botocore.exceptions import BotoCoreError, ClientError
from datetime import timedelta
from dateutil import parser as dateparser

from sat_ingest.core.adapters.base import CatalogAdapter
from sat_ingest.core.search import SearchParams
from sat_ingest.core.models import Item, Asset
from sat_ingest.core.storage.local import LocalSink
from sat_ingest.core.http import HttpClient

DEFAULT_BUCKETS = {
    "goes-16": "noaa-goes16",
    "goes-17": "noaa-goes17",
    "goes-18": "noaa-goes18",
}

_DEFAULT_SAMPLE_URI = os.environ.get("GOES_SAMPLE_URI", "s3://noaa-goes16/README.txt")


@dataclass
class GoesSearchConfig:
    satellite: str = "goes-16"
    product_prefix: str = "ABI-L2-CMIPF"


class NoaaGoesAdapter(CatalogAdapter):
    name = "NOAA GOES (AWS S3)"

    def __init__(
        self,
        data_root: str | None = None,
        satellite: str = "goes-16",
        product_prefix: str = "ABI-L2-CMIPF",
        sample_uri: str | None = None,
    ):
        self.sink = LocalSink(root=data_root)
        self.satellite = satellite.lower()
        self.product_prefix = product_prefix
        self.bucket = DEFAULT_BUCKETS.get(self.satellite, "noaa-goes16")
        self.s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        self.http = HttpClient()
        self.sample_uri = sample_uri or _DEFAULT_SAMPLE_URI

    def _iter_s3_keys(self, prefix: str, max_keys: int) -> Iterable[str]:
        paginator = self.s3.get_paginator("list_objects_v2")
        count = 0
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield obj["Key"]
                count += 1
                if count >= max_keys:
                    return

    def _media_type_for_key(self, key: str) -> str:
        return "application/netcdf" if key.lower().endswith(".nc") else "application/octet-stream"

    def _yield_stub_item(self) -> Iterable[Item]:
        item_id = f"{self.satellite}-stub"
        assets = {
            "sample": Asset(
                key="sample",
                href=self.sample_uri,
                media_type=self._media_type_for_key(self.sample_uri),
            )
        }
        yield Item(
            id=item_id,
            collection=f"{self.satellite}-{self.product_prefix}".lower(),
            datetime=None,
            bbox=None,
            geometry=None,
            assets=assets,
            properties={
                "note": "stub item from noaa_goes adapter; provide --time to list real S3 keys",
                "s3_bucket": self.bucket,
            },
        )

    def search(self, params: SearchParams) -> Iterable[Item]:
        if not params.time:
            yield from self._yield_stub_item()
            return

        try:
            start_s, end_s = params.time.split("/")
            start = dateparser.isoparse(start_s)
            end = dateparser.isoparse(end_s)
        except Exception as e:
            print(f"[noaa_goes] invalid time format: {params.time}", file=sys.stderr)
            yield from self._yield_stub_item()
            return

        limit = params.limit or 10
        count = 0
        current = start
        while current <= end and count < limit:
            year = current.year
            yday = int(current.strftime("%j"))
            hour = current.hour
            prefix = f"abi/L2/CMIPF/{year:04d}/{yday:03d}/{hour:02d}/"
            try:
                for key in self._iter_s3_keys(prefix, max_keys=limit - count):
                    item_id = os.path.basename(key)
                    assets = {
                        "data": Asset(
                            key="data",
                            href=f"s3://{self.bucket}/{key}",
                            media_type=self._media_type_for_key(key),
                        )
                    }
                    yield Item(
                        id=item_id,
                        collection=f"{self.satellite}-{self.product_prefix}".lower(),
                        datetime=None,
                        bbox=None,
                        geometry=None,
                        assets=assets,
                        properties={"s3_bucket": self.bucket, "s3_key": key, "prefix": prefix},
                    )
                    count += 1
                    if count >= limit:
                        break
            except Exception as e:
                print(f"[noaa_goes] listing failed for {prefix}: {e}", file=sys.stderr)
            current += timedelta(hours=1)

        if count == 0:
            yield from self._yield_stub_item()

    def item(self, item_id: str) -> Optional[Item]:
        return None

    def download(self, item: Item, asset_keys: Optional[Sequence[str]] = None, **kwargs) -> Dict[str, Asset]:
        selected = asset_keys or list(item.assets.keys())
        out: Dict[str, Asset] = {}
        for k in selected:
            if k not in item.assets:
                print(f"Warning: asset '{k}' not found on item {item.id}; skipping.", file=sys.stderr)
                continue

            asset = item.assets[k]
            href = asset.href
            basename = os.path.basename(href) if href.startswith("s3://") else k
            filename = basename if os.path.splitext(basename)[1] else k

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name

            ok = True
            try:
                self.http.stream_download(href, tmp_path, chunk_size=1024 * 512, on_chunk=None)
            except Exception as e:
                ok = False
                try:
                    with open(tmp_path, "wb") as f:
                        f.write(
                            (
                                "NOAA GOES adapter stub placeholder.\n"
                                f"Requested: {href}\n"
                                f"Reason: {e.__class__.__name__}: {e}\n"
                            ).encode("utf-8")
                        )
                except Exception:
                    pass

            dest_key = f"{item.collection}/{item.id}/{filename}"
            dest_path = self.sink.put(tmp_path, dest_key)
            asset.local_path = dest_path
            out[k] = asset

            try:
                os.remove(tmp_path)
            except OSError:
                pass

            if ok:
                print(f"Copied {href} -> {dest_path}")
            else:
                print(f"Created placeholder for {href} -> {dest_path}", file=sys.stderr)

        return out



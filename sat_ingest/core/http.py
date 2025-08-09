# import httpx
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# _DEFAULT_TIMEOUT = httpx.Timeout(30.0)

# class HttpClient:
#     """Shared HTTP client with retries and timeouts."""

#     def __init__(self, headers: dict | None = None):
#         self._client = httpx.Client(headers=headers or {}, timeout=_DEFAULT_TIMEOUT)

#     @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, max=10),
#            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError)))
#     def get(self, url: str, **kwargs) -> httpx.Response:
#         resp = self._client.get(url, **kwargs)
#         resp.raise_for_status()
#         return resp

#     @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, max=10),
#            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError)))
#     def post(self, url: str, json: dict, **kwargs) -> httpx.Response:
#         resp = self._client.post(url, json=json, **kwargs)
#         resp.raise_for_status()
#         return resp

#     def stream_download(self, url: str, dest_path: str, chunk_size: int = 1024 * 1024):
#         with self._client.stream("GET", url) as r:
#             r.raise_for_status()
#             with open(dest_path, "wb") as f:
#                 for chunk in r.iter_bytes(chunk_size=chunk_size):
#                     f.write(chunk)

# # sat_ingest/core/http.py
# import httpx
# from typing import Optional, Callable
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# _DEFAULT_TIMEOUT = httpx.Timeout(30.0)

# class HttpClient:
#     """Shared HTTP client with retries and timeouts."""

#     def __init__(self, headers: dict | None = None):
#         self._client = httpx.Client(headers=headers or {}, timeout=_DEFAULT_TIMEOUT)

#     @retry(
#         stop=stop_after_attempt(5),
#         wait=wait_exponential(multiplier=0.5, max=10),
#         retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError))
#     )
#     def get(self, url: str, **kwargs) -> httpx.Response:
#         resp = self._client.get(url, **kwargs)
#         resp.raise_for_status()
#         return resp

#     @retry(
#         stop=stop_after_attempt(5),
#         wait=wait_exponential(multiplier=0.5, max=10),
#         retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError))
#     )
#     def post(self, url: str, json: dict, **kwargs) -> httpx.Response:
#         resp = self._client.post(url, json=json, **kwargs)
#         resp.raise_for_status()
#         return resp

#     def stream_download(
#         self,
#         url: str,
#         dest_path: str,
#         chunk_size: int = 1024 * 1024,
#         on_chunk: Optional[Callable[[int, Optional[int]], None]] = None,
#     ):
#         """
#         Stream a URL to disk. If provided, `on_chunk(bytes_read, total_bytes_or_None)`
#         is called after each chunk to support progress updates.
#         """
#         with self._client.stream("GET", url) as r:
#             r.raise_for_status()
#             total = None
#             try:
#                 total = int(r.headers.get("Content-Length")) if r.headers.get("Content-Length") else None
#             except (TypeError, ValueError):
#                 total = None
#             with open(dest_path, "wb") as f:
#                 for chunk in r.iter_bytes(chunk_size=chunk_size):
#                     f.write(chunk)
#                     if on_chunk:
#                         on_chunk(len(chunk), total)










# sat_ingest/core/http.py
import httpx
from typing import Optional, Callable, Tuple, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# NEW
from urllib.parse import urlparse
from .auth import AwsConfig

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore import UNSIGNED
    from botocore.exceptions import ClientError, NoCredentialsError
except Exception:  # pragma: no cover
    boto3 = None

_DEFAULT_TIMEOUT = httpx.Timeout(30.0)

class HttpClient:
    """Shared HTTP client with retries and timeouts."""

    def __init__(self, headers: dict | None = None, aws: AwsConfig | None = None):
        self._client = httpx.Client(headers=headers or {}, timeout=_DEFAULT_TIMEOUT)
        self._aws = aws  # optional explicit AWS config

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError))
    )
    def get(self, url: str, **kwargs) -> httpx.Response:
        resp = self._client.get(url, **kwargs)
        resp.raise_for_status()
        return resp

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError))
    )
    def post(self, url: str, json: dict, **kwargs) -> httpx.Response:
        resp = self._client.post(url, json=json, **kwargs)
        resp.raise_for_status()
        return resp

    # -------- S3 helpers ----------------------------------------------------
    def _make_boto_clients(self) -> List:
        """
        Build a list of S3 clients to try, in order:
        1) unsigned (public access)
        2) signed using explicit AwsConfig (if provided)
        3) signed using default Boto session (env/profile/IMDS)
        """
        if boto3 is None:
            raise RuntimeError("boto3 is required for s3:// downloads (pip install boto3).")

        clients = [boto3.client("s3", config=BotoConfig(signature_version=UNSIGNED))]

        # Explicit config if caller provided it
        if self._aws:
            if self._aws.profile:
                session = boto3.Session(profile_name=self._aws.profile, region_name=self._aws.region)
                clients.append(session.client("s3"))
            elif self._aws.access_key_id and self._aws.secret_access_key:
                session = boto3.Session(
                    aws_access_key_id=self._aws.access_key_id,
                    aws_secret_access_key=self._aws.secret_access_key,
                    aws_session_token=self._aws.session_token,
                    region_name=self._aws.region,
                )
                clients.append(session.client("s3"))

        # Default session last (env vars, AWS_PROFILE, EC2/ECS role, etc.)
        clients.append(boto3.client("s3"))
        return clients

    def _s3_get_object(self, s3, bucket: str, key: str, allow_requester_pays: bool) -> dict:
        try:
            return s3.get_object(Bucket=bucket, Key=key)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if allow_requester_pays and code in ("RequestPaymentRequired", "AccessDenied"):
                # Retry with RequestPayer=requester (still requires credentials)
                return s3.get_object(Bucket=bucket, Key=key, RequestPayer="requester")
            raise

    def _stream_s3(
        self,
        s3_url: str,
        dest_path: str,
        chunk_size: int,
        on_chunk: Optional[Callable[[int, Optional[int]], None]],
    ):
        parsed = urlparse(s3_url)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        aws = self._aws or AwsConfig.from_env()
        clients = self._make_boto_clients()

        last_err: Exception | None = None
        for s3 in clients:
            try:
                obj = self._s3_get_object(s3, bucket, key, allow_requester_pays=aws.requester_pays)
            except (ClientError, NoCredentialsError) as e:
                last_err = e
                continue

            total = obj.get("ContentLength")
            body = obj["Body"]
            with open(dest_path, "wb") as f:
                it = getattr(body, "iter_chunks", None)
                if callable(it):
                    for chunk in body.iter_chunks(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        if on_chunk:
                            on_chunk(len(chunk), total)
                else:
                    while True:
                        chunk = body.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        if on_chunk:
                            on_chunk(len(chunk), total)
            return  # success

        # If none of the clients worked, raise the last error with a friendlier hint
        hint = ""
        if isinstance(last_err, NoCredentialsError):
            hint = (
                "\nHint: Provide AWS credentials (env vars or profile) "
                "or pass AwsConfig(profile=..., ...) to HttpClient(...)."
            )
        raise RuntimeError(f"Failed to download {s3_url} from S3: {last_err}{hint}")

    # -------- Public download API -------------------------------------------
    def stream_download(
        self,
        url: str,
        dest_path: str,
        chunk_size: int = 1024 * 1024,
        on_chunk: Optional[Callable[[int, Optional[int]], None]] = None,
    ):
        """
        Stream a URL (HTTP(S) or S3) to disk.

        If provided, `on_chunk(bytes_read, total_bytes_or_None)` is called after each chunk.
        """
        if url.startswith("s3://"):
            return self._stream_s3(url, dest_path, chunk_size, on_chunk)

        with self._client.stream("GET", url) as r:
            r.raise_for_status()
            total = None
            try:
                total = int(r.headers.get("Content-Length")) if r.headers.get("Content-Length") else None
            except (TypeError, ValueError):
                total = None
            with open(dest_path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=chunk_size):
                    f.write(chunk)
                    if on_chunk:
                        on_chunk(len(chunk), total)



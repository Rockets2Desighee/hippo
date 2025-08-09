# from __future__ import annotations
# import os
# import shutil
# from .base import StorageSink

# class LocalSink(StorageSink):
#     # def __init__(self, root: str = "./data"):
#     #     self.root = root
#     #     os.makedirs(self.root, exist_ok=True)
    

#     # Stores files locally on computer, as a proxy for the s3 bucket that users can store extracted data into.
#     def __init__(self, root: str | None = None):
#         # NEW: allow env var, default to ./data
#         root = root or os.environ.get("SAT_DATA_ROOT", "./data")
#         self.root = os.path.expanduser(root)  # handle ~/sat-data
#         os.makedirs(self.root, exist_ok=True)

#     def put(self, src_path: str, dest_key: str) -> str:
#         dest = os.path.join(self.root, dest_key)
#         os.makedirs(os.path.dirname(dest), exist_ok=True)
#         shutil.copy2(src_path, dest)
#         return dest

from __future__ import annotations
import os
import shutil
from .base import StorageSink

class LocalSink(StorageSink):
    """
    Stores files locally on your machine, acting as a stand-in for the future S3 bucket.
    Honors SAT_DATA_ROOT (e.g., SAT_DATA_ROOT=~/sat-data). Defaults to ./data.
    """

    def __init__(self, root: str | None = None):
        # Allow env var, default to ./data; handle ~/... paths.
        root = root or os.environ.get("SAT_DATA_ROOT", "./data")
        self.root = os.path.expanduser(root)
        os.makedirs(self.root, exist_ok=True)

    def put(self, src_path: str, dest_key: str) -> str:
        """
        Copy a local file into the repository under the data root using dest_key as the relative path.
        Returns the absolute destination path.
        """
        dest = os.path.join(self.root, dest_key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src_path, dest)
        return dest



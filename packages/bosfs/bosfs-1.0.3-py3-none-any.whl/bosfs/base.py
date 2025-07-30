"""
"""

import logging
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

from fsspec.spec import AbstractFileSystem
from fsspec.utils import stringify_path

from .file import BOSFile

from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos.bos_client import BosClient

logger = logging.getLogger("bosfs")
logging.getLogger("baidubce.http.bce_http_client").setLevel(logging.WARNING)

DEFAULT_POOL_SIZE = 20
DEFAULT_BLOCK_SIZE = 16 * 2**20
SIMPLE_TRANSFER_THRESHOLD = 5 * 2**30

class BaseBOSFileSystem(AbstractFileSystem):
    """
    Access BOS as if it were a file system.

    This exposes a filesystem-like API (ls, cp, open, etc.) on top of BOS storage.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        sts_token: Optional[str] = None,
        default_cache_type: str = "readahead",
        default_block_size: Optional[int] = None,
        **kwargs,
    ):
        """
        Parameters
        ----------
        endpoint : str, optional
            The URL to the BOS service. If not provided, will be inferred from the credentials.
        access_key : str, optional
            The access key for the BOS account. If not provided, will be inferred from the credentials.
        secret_key : str, optional
            The secret key for the BOS account. If not provided, will be inferred from the credentials.
        sts_token : str, optional
            The sts_token for the BOS account. If not provided, will be inferred from the credentials.
        default
        """
        self._access_key = access_key or os.getenv("BCE_ACCESS_KEY_ID")
        self._secret_key = secret_key or os.getenv("BCE_SECRET_ACCESS_KEY")
        self._endpoint = endpoint or os.getenv("BOS_ENDPOINT")
        self._bce_client_config = BceClientConfiguration(credentials=BceCredentials(self._access_key,
            self._secret_key), endpoint=self._endpoint, security_token=sts_token)

        super_kwargs = {
            k: kwargs.pop(k)
            for k in ["use_listings_cache", "listings_expiry_time", "max_paths"]
            if k in kwargs
        }  # passed to fsspec superclass
        super().__init__(**super_kwargs)

        self._default_block_size = default_block_size or DEFAULT_BLOCK_SIZE
        self._default_cache_type = default_cache_type

    def set_endpoint(self, endpoint: str):
        """
        Reset the endpoint for bosfs
        endpoint : string (None)
            Default endpoints of the fs
            Endpoints are the address where BOS locate
            like: http://bj.bcebos.com
        """
        if not endpoint:
            raise ValueError("Not a valid endpoint")
        self._endpoint = endpoint

    @classmethod
    def _strip_protocol(cls, path):
        """Turn path from fully-qualified to file-system-specifi
        Parameters
        ----------
        path : Union[str, List[str]]
            Input path, like
            `http://bj.bcebos.com/mybucket/myobject`
            `bos://mybucket/myobject`
        Examples
        --------
        >>> _strip_protocol(
            "http://bj.bcebos.com/mybucket/myobject"
            )
        ('mybucket/myobject')
        >>> _strip_protocol(
            "bos://mybucket/myobject"
            )
        ('mybucket/myobject')
        """
        if isinstance(path, list):
            return [cls._strip_protocol(p) for p in path]
        path_string: str = stringify_path(path)
        if path_string.startswith("bos://"):
            path_string = path_string[6:]
        
        parser_re = r"https?://(?P<endpoint>[a-z]+\.bcebos\.com)/(?P<path>.+)"
                                                                
        matcher = re.compile(parser_re).match(path_string)
        if matcher:
            path_string = matcher["path"]
        return path_string or cls.root_marker

    def split_path(self, path: str) -> Tuple[str, str]:
        """
        Normalise object path string into bucket and key.
        Parameters
        ----------
        path : string
            Input path, like `/mybucket/path/to/file`
        Examples
        --------
        >>> split_path("/mybucket/path/to/file")
        ['mybucket', 'path/to/file' ]
        >>> split_path("
        /mybucket/path/to/versioned_file?versionId=some_version_id
        ")
        ['mybucket', 'path/to/versioned_file', 'some_version_id']
        """
        path = self._strip_protocol(path)
        path = path.lstrip("/")
        if "/" not in path:
            return path, ""
        bucket_name, obj_name = path.split("/", 1)
        return bucket_name, obj_name

    def invalidate_cache(self, path: Optional[str] = None):
        if path is None:
            self.dircache.clear()
        else:
            norm_path: str = self._strip_protocol(path)
            norm_path = norm_path.lstrip("/")
            self.dircache.pop(norm_path, None)
            while norm_path:
                self.dircache.pop(norm_path, None)
                norm_path = self._parent(norm_path)

    def _transfer_object_info_to_dict(
        self, bucket: str, obj, is_file: bool = True
    ) -> Dict:
        data = None
        if is_file:
            data: Dict[str, Any] = {
                "name": f"{bucket}/{obj.key}",
                "type": "file",
                "size": obj.size,
            }
        else:
            data: Dict[str, Any] = {
                "name": f"{bucket}/{obj.prefix}",
                "type": "directory",
                "size": 0,
            }
        if obj.last_modified:
            data["LastModified"] = obj.last_modified            
        return data

    def _verify_find_arguments(
        self, path: str, maxdepth: Optional[int], withdirs: bool, prefix: str
    ) -> str:
        path = self._strip_protocol(path)
        bucket, _ = self.split_path(path)
        if not bucket:
            raise ValueError("Cannot traverse all of the buckets")
        if (withdirs or maxdepth) and prefix:
            raise ValueError(
                "Can not specify 'prefix' option alongside "
                "'withdirs'/'maxdepth' options."
            )
        return path

    def _get_batch_delete_key_list(self, pathlist: List[str]) -> Tuple[str, List[str]]:
        buckets: Set[str] = set()
        key_list: List[str] = []
        for path in pathlist:
            bucket, key = self.split_path(path)
            buckets.add(bucket)
            if not key:
                continue
            key_list.append(key)
        if len(buckets) > 1:
            raise ValueError("Bulk delete files should refer to only one bucket")
        bucket = buckets.pop()
        if len(pathlist) > 1000:
            raise ValueError("Max number of files to delete in one call is 1000")
        for path in pathlist:
            self.invalidate_cache(self._parent(path))
        return bucket, key_list

    def _open(
        self,
        path: str,
        mode: str = "rb",
        block_size: Optional[int] = 4 * 2**20, # 4MB is good for append
        autocommit: bool = True,
        cache_options: Optional[str] = None,
        **kwargs,
    ) -> "BOSFile":
        """
        Open a file for reading or writing.
        Parameters
        ----------
        path: str
            File location
        mode: str
            'rb', 'wb', etc.
        autocommit: bool
            If False, writes to temporary file that only gets put in final
            location upon commit
        kwargs
        Returns
        -------
        BOSFile instance
        """
        cache_type = kwargs.pop("cache_type", self._default_cache_type)
        return BOSFile(
            self,
            path,
            mode,
            block_size,
            autocommit,
            cache_options=cache_options,
            cache_type=cache_type,
            **kwargs,
        )
    
    def touch(self, path: str, truncate: bool = True, **kwargs):
        """Create empty file, or update timestamp

        Parameters
        ----------
        path: str
            file location
        truncate: bool
            If True, always set file size to 0; if False, update timestamp and
            leave file unchanged, if backend allows this
        """
        if truncate or not self.exists(path):
            self.invalidate_cache(self._parent(path))
            with self.open(path, "wb", **kwargs):
                pass
        else:
            raise NotImplementedError

    
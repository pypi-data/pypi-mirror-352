"""
"""

import copy
import logging
import os
from datetime import datetime
from hashlib import sha256
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from baidubce.auth.bce_credentials import BceCredentials
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos.bos_client import BosClient

from .base import DEFAULT_BLOCK_SIZE, SIMPLE_TRANSFER_THRESHOLD, BaseBOSFileSystem
from .utils import as_progress_handler, prettify_info_result, base64_md5
from .exceptions import translate_bos_error

logger = logging.getLogger("bosfs")

class BOSFileSystem(BaseBOSFileSystem):
    """
    A pythonic file-systems interface to BOS
    """

    def __init__(self, **kwargs):
        self._bos_client = None
        super().__init__(**kwargs)

    def _get_client(self) -> BosClient:
        """
        get the bos client instance
        """
        if self._bos_client is not None:
            return self._bos_client
        if not self._bce_client_config:
            raise ValueError("ak/ak/endpoint is required")
        try:
            self._bos_client = BosClient(self._bce_client_config)
            return self._bos_client
        except exception.BceError as err:
            raise RuntimeError(f"Failed to create BOS client: {err.last_error}") from err

    def _ls_bucket(self) -> List[Dict[str, Any]]:
        if "" not in self.dircache:
            results: List[Dict[str, Any]] = []
            try:
                for bucket in self._get_client().list_buckets().buckets:
                    result = {
                        "name": bucket.name,
                        "type": "directory",
                        "size": 0,
                        "CreateTime": bucket.creation_date,
                    }
                    results.append(result)
            except exception.BceError:
                pass
            self.dircache[""] = copy.deepcopy(results)
        else:
            results = self.dircache[""]
        return results

    def _get_object_info_list(
        self,
        bucket_name: str,
        prefix: str,
        delimiter: str,
    ):
        """
        Wrap bos object return values into a fsspec form of file info
        """
        result = []
        marker = None
        try:
            while True:
                response = self._get_client().list_objects(
                    bucket_name, marker=marker, prefix=prefix, delimiter=delimiter)
                for item in response.contents or []:
                    data = self._transfer_object_info_to_dict(bucket_name, item, True)
                    result.append(data)
                for item in response.common_prefixes or []:
                    data = self._transfer_object_info_to_dict(bucket_name, item, False)
                    result.append(data)
                if response.is_truncated:
                    marker = response.next_marker
                else:
                    break
        except exception.BceError as err:
            raise translate_bos_error(err)
        return result

    def _ls_dir(
        self,
        path: str,
        delimiter: str = "/",
        refresh: bool = False,
        prefix: str = "",
    ) -> List[Dict]:
        norm_path = path.strip("/")
        if norm_path in self.dircache and not refresh and not prefix and delimiter:
            return self.dircache[norm_path]

        logger.debug("Get directory listing page for %s", norm_path)
        bucket_name, key = self.split_path(norm_path)
        if not delimiter or prefix:
            if key:
                prefix = f"{key}/{prefix}"
        else:
            if norm_path in self.dircache and not refresh:
                return self.dircache[norm_path]
            if key:
                prefix = f"{key}/"

        try:
            self.dircache[norm_path] = self._get_object_info_list(
                bucket_name, prefix, delimiter
            )
            return self.dircache[norm_path]
        except exception.BceError as err:
            raise translate_bos_error(err)

    @prettify_info_result
    def ls(self, path: str, detail: bool = True, **kwargs):
        norm_path = self._strip_protocol(path).strip("/")
        if norm_path == "":
            return self._ls_bucket()
        files = self._ls_dir(path)
        if not files and "/" in norm_path:
            files = self._ls_dir(self._parent(path))
            files = [
                file
                for file in files
                if file["type"] != "directory" and file["name"].strip("/") == norm_path
            ]

        return files
    
    @prettify_info_result
    def find(
        self,
        path: str,
        maxdepth: Optional[int] = None,
        withdirs: bool = False,
        detail: bool = False,
        **kwargs,
    ):
        """List all files below path.

        Like posix ``find`` command without conditions

        Parameters
        ----------
        path : str
        maxdepth: int or None
            If not None, the maximum number of levels to descend
        withdirs: bool
            Whether to include directory paths in the output. This is True
            when used by glob, but users usually only want files.
        kwargs are passed to ``ls``.
        """
        out = {}
        prefix = kwargs.pop("prefix", "")
        path = self._verify_find_arguments(path, maxdepth, withdirs, prefix)
        if prefix:
            for info in self._ls_dir(
                path, delimiter="", prefix=prefix
            ):
                out.update({info["name"]: info})
        else:
            for _, dirs, files in self.walk(path, maxdepth, detail=True, **kwargs):
                if withdirs:
                    files.update(dirs)
                out.update({info["name"]: info for name, info in files.items()})
            if self.isfile(path) and path not in out:
                # walk works on directories, but find should also return [path]
                # when path happens to be a file
                out[path] = {}
        names = sorted(out)
        return {name: out[name] for name in names}

    def _directory_exists(self, dirname: str, **kwargs):
        ls_result = self._ls_dir(dirname)
        return bool(ls_result)
    
    def _file_exists(self, bucket_name: str, filename: str):
        try:
            response = self._get_client().get_object_meta_data(bucket_name, filename)
            return True
        except exception.BceError as e:
            return False

    def _bucket_exist(self, bucket_name: str):
        if not bucket_name:
            return False
        try:
            return self._get_client().does_bucket_exist(bucket_name)
        except exception.BceError:
            return False

    def exists(self, path: str, **kwargs) -> bool:
        """Is there a file at the given path"""
        norm_path = self._strip_protocol(path).lstrip("/")
        if norm_path == "":
            return True

        bucket_name, obj_name = self.split_path(path)

        if not self._bucket_exist(bucket_name):
            return False

        if not obj_name:
            return True

        if self._file_exists(bucket_name, obj_name):
            return True

        return self._directory_exists(path)

    def ukey(self, path: str):
        """Hash of file properties, to tell if it has changed"""
        bucket_name, obj_name = self.split_path(path)
        try:
            response = self._get_client().get_object_meta_data(bucket_name, obj_name)
        except exception.BceError as err:
            raise translate_bos_error(err)
        return response.metadata.bce_content_crc_32

    def checksum(self, path: str):
        """Unique value for current version of file

        If the checksum is the same from one moment to another, the contents
        are guaranteed to be the same. If the checksum changes, the contents
        *might* have changed.

        This should normally be overridden; default will probably capture
        creation/modification timestamp (which would be good) or maybe
        access timestamp (which would be bad)
        """
        return sha256(
            (str(self.ukey(path)) + str(self.info(path))).encode()
        ).hexdigest()

    def cp_file(self, src_path: str, target_path: str, **kwargs):
        """
        Copy within two locations in the filesystem
        # todo: big file optimization
        """
        source_bucket_name, source_object_key = self.split_path(src_path)
        target_bucket_name, target_object_key = self.split_path(target_path)
        self.invalidate_cache(self._parent(target_path))
        try:
            self._get_client().copy_object(source_bucket_name, source_object_key, 
                target_bucket_name, target_object_key)
        except exception.BceError as err:
            raise translate_bos_error(err)

    def _rm(self, path: Union[str, List[str]]):
        """Delete files.

        Parameters
        ----------
        path: str or list of str
            File(s) to delete.
        """
        if isinstance(path, list):
            for file in path:
                self._rm(file)
            return
        bucket_name, obj_name = self.split_path(path)
        self.invalidate_cache(self._parent(path))
        try:
            self._get_client().delete_object(bucket_name, obj_name)
        except exception.BceError as err:
            raise translate_bos_error(err)
        

    def _bulk_delete(self, pathlist, **kwargs):
        """
        Remove multiple keys with one call

        Parameters
        ----------
        pathlist : list(str)
            The keys to remove, must all be in the same bucket.
            Must have 0 < len <= 1000
        """
        if not pathlist:
            return
        bucket_name, key_list = self._get_batch_delete_key_list(pathlist)
        if len(key_list) > 1000:
            raise ValueError("Cannot bulk delete more than 1000 objects.")
        if len(key_list) == 0:
            return
        try:
            self._get_client().delete_multiple_objects(bucket_name, key_list)
        except exception.BceError as err:
            raise translate_bos_error(err)

    def rm(self, path: Union[str, List[str]], recursive=False, maxdepth=None):
        """Delete files.

        Parameters
        ----------
        path: str or list of str
            File(s) to delete.
        recursive: bool
            If file(s) are directories, recursively delete contents and then
            also remove the directory
        maxdepth: int or None
            Depth to pass to walk for finding files to delete, if recursive.
            If None, there will be no limit and infinite recursion may be
            possible.
        """

        if isinstance(path, list):
            for file in path:
                self.rm(file)
            return

        path_expand = self.expand_path(path, recursive=recursive, maxdepth=maxdepth)

        def chunks(lst: list, num: int):
            for i in range(0, len(lst), num):
                yield lst[i : i + num]

        for files in chunks(path_expand, 1000):
            self._bulk_delete(files)

    def get_path(self, rpath: str, lpath: str, **kwargs):
        """
        Copy single remote path to local
        """
        if self.isdir(rpath):
            os.makedirs(lpath, exist_ok=True)
        else:
            self.get_file(rpath, lpath, **kwargs)

    def get_file(
        self, rpath: str, lpath: str, callback: Optional[Callable] = None, **kwargs
    ):
        """
        Copy single remote file to local
        """
        bucket_name, obj_name = self.split_path(rpath)

        if self.isdir(rpath):
            os.makedirs(lpath, exist_ok=True)
            return
        try:
            self._get_client().get_object_to_file(bucket_name, obj_name, lpath, 
                progress_callback=as_progress_handler(callback))
        except exception.BceError as err:
            raise translate_bos_error(err)

    def put_file(
        self, lpath: str, rpath: str, callback: Optional[Callable] = None, **kwargs
    ):
        """
        Copy single file to remote
        """
        bucket_name, obj_name = self.split_path(rpath)
        if os.path.isdir(lpath):
            if obj_name:
                # don't make remote "directory"
                return
            self.mkdir(lpath)
        else:
            try:
                if os.path.getsize(lpath) >= SIMPLE_TRANSFER_THRESHOLD:
                    self._get_client().put_super_obejct_from_file(bucket_name, obj_name, lpath, 
                        progress_callback=as_progress_handler(callback))
                else:
                    self._get_client().put_object_from_file(bucket_name, obj_name, lpath, 
                        progress_callback=as_progress_handler(callback))
            except exception.BceError as err:
                raise translate_bos_error(err)
        self.invalidate_cache(self._parent(rpath))

    def created(self, path: str):
        """Return the created timestamp of a file as a datetime.datetime"""
        raise NotImplementedError("BOS has no created timestamp")

    def modified(self, path: str):
        """Return the modified timestamp of a file as a datetime.datetime"""
        bucket_name, obj_name = self.split_path(path)
        if not obj_name or self.isdir(path):
            raise NotImplementedError("bucket has no modified timestamp")
        try:
            response = self._get_client().get_object_meta_data(bucket_name, obj_name)
        except exception.BceError as err:
            raise translate_bos_error(err)
        return int(
            datetime.strptime(
                response.metadata.last_modified,
                "%a, %d %b %Y %H:%M:%S %Z",
            ).timestamp()
        )

    def append_object(self, path: str, location: int, value: bytes) -> int:
        """
        Append bytes to the object
        """
        offset = None
        if int(location) > 0:
            offset = location
        bucket_name, obj_name = self.split_path(path)
        try:
            response = self._get_client().append_object(bucket_name=bucket_name, 
                                     key=obj_name,
                                     data=value,
                                     content_md5=base64_md5(value), 
                                     content_length=len(value),
                                     offset=offset)
            return response.metadata.bce_next_append_offset
        except exception.BceError as err:
            raise translate_bos_error(err)

    def get_object(self, path: str, start: int, end: int) -> bytes:
        """
        Return object bytes in range
        """
        bucket_name, obj_name = self.split_path(path)
        try:
            data = self._get_client().get_object_as_string(bucket_name, obj_name, range=[start, end])
            return data
        except exception.BceError as err:
            raise translate_bos_error(err)
        
    def sign(self, path: str, expiration: int = 100, **kwargs):
        raise NotImplementedError("Sign is not implemented for this filesystem")

    def pipe_file(self, path: str, value: str, **kwargs):
        """Set the bytes of given file"""
        bucket_name, obj_name = self.split_path(path)
        block_size = kwargs.get("block_size", DEFAULT_BLOCK_SIZE)
        # 5 GB is the limit for an BOS PUT
        self.invalidate_cache(path)
        try:
            if len(value) < min(5 * 2**30, 10 * block_size):
                self._get_client().put_object_from_string(bucket_name, obj_name, value)
                return
            raise NotImplementedError("Sign is not implemented for this filesystem")
            upload_id = self._get_client().initiate_multipart_upload(bucket_name, obj_name).upload_id
            part_list = []
            for i, off in enumerate(range(0, len(value), block_size)):
                data = value[off : off + block_size]
                part_number = i + 1
                response = self._get_client().upload_part_from_file(bucket_name, obj_name, 
                                upload_id, part_number, len(data), data, offset)
                part_list.append(
                    {
                        "partNumber": part_number,
                        "eTag": response.metadata.etag
                    }
                )
            self._get_client().complete_multipart_upload(bucket_name, obj_name, upload_id, part_list)
        except exception.BceError as err:
            raise translate_bos_error(err)


    @prettify_info_result
    def info(self, path, **kwargs):
        #path = path.rstrip("/")
        bucket_name, obj_name = self.split_path(path)
        if not bucket_name:
            return {"name": f"/", "size": 0, "type": "directory"}
        if len(bucket_name) <= 3:
            raise FileNotFoundError
        if not obj_name:
            exists = self._get_client().does_bucket_exist(bucket_name)
            if not exists:
                raise FileNotFoundError
            return {"name": f"{bucket_name}/", "size": 0, "type": "directory"}
        try:
            response = self._get_client().get_object_meta_data(bucket_name, obj_name)
            return {
                "name": f"{bucket_name}/{obj_name}",
                "size": int(response.metadata.content_length),
                "type": "file" if not obj_name.endswith("/") else "directory",
                "LastModified": datetime.strptime(response.metadata.last_modified, 
                    "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        except exception.BceError as err:
            if err.status_code == 404:
                if not obj_name.endswith("/"):
                    obj_name += "/"
                try:
                    response = self._get_client().list_objects(bucket_name, 
                        prefix=obj_name, max_keys=2)
                    if response.contents:
                        return {"name": f"{bucket_name}/{obj_name.rstrip('/')}", "size": 0, "type": "directory"}
                except exception.BceError as err:
                    raise translate_bos_error(err)
            else:
                raise translate_bos_error(err)
        raise FileNotFoundError
        
    
    def cat_file(
        self,
        path: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ):
        bucket_name, obj_name = self.split_path(path)
        read_range = None
        if start and end:
            read_range = [start, end]
        try:
            data = self._get_client().get_object_as_string(bucket_name, obj_name, range=read_range)
        except exception.BceError as err:
            raise translate_bos_error(err)
        return data


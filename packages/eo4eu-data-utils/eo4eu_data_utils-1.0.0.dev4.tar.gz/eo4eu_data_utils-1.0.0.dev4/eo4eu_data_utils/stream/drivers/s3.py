from pathlib import Path
from eo4eu_base_utils import OptionalModule, if_none
from eo4eu_base_utils.typing import Any, Callable, Self, List, Dict

from ..model import PathSpec, Downloader, Uploader, Lister
from ...settings import Settings


_s3_module = OptionalModule(
    package = "eo4eu_data_utils",
    enabled_by = ["s3", "full"],
    depends_on = ["boto3"]
)


if _s3_module.is_enabled():
    import boto3

    class S3Driver(Downloader, Uploader, Lister):
        """Implements :class:`eo4eu_data_utils.stream.Downloader`, :class:`eo4eu_data_utils.stream.Uploader`
        and :class:`eo4eu_data_utils.stream.Lister` for S3 related operations. Warning: You must enable
        S3 support to use this class by doing either ``pip install eo4eu_data_utils[s3]`` or 
        ``pip install eo4eu_data_utils[full]``.

        :param config: The boto3 config dict for the underlying :class:`boto3.resource` (Refer to https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
        :type config: Dict[str,Any]
        :param bucket: The bucket the driver will refer to. If it doesn't exist, the driver will attempt to create it.
        :type bucket: str
        :param ls_func: An optional function for converting boto3 S3.ServiceResource.ObjectSummary objects to PathSpec objects (default: uses the ``.key`` attribute of the ObjectSummary as path, and the ``.key`` attribute relative to the passed prefix as name)
        :type ls_func: Callable[[S3.ServiceResource.ObjectSummary,Path],PathSpec]|None
        """

        def __init__(
            self,
            config: Dict[str,Any],
            bucket: str,
            ls_func: Callable[[Any],PathSpec]|None = None
        ):
            ls_func = if_none(ls_func, lambda summary, prefix: PathSpec(
                name = Path(summary.key).relative_to(prefix),
                path = Path(summary.key),
                meta = {}
            ))

            extra_config = None
            try:  # Fix an S3 configuration update that caused requests to fail
                from botocore.config import Config
                from importlib.metadata import version

                for boto_part, lower_part in zip(version("boto3").split("."), "1.35.99".split(".")):
                    if int(boto_part) > int(lower_part):
                        extra_config = Config(request_checksum_calculation = "when_required")
                        break
            except Exception as e:
                Settings.LOGGER.warning(f"Failed to modify S3Driver configuration: {e}")

            if extra_config is None or "config" in config:
                self.resource = boto3.resource("s3", **config)
            else:
                self.resource = boto3.resource("s3", **config, config = extra_config)

            self.bucket = self.resource.Bucket(bucket)
            self.bucket_name = bucket
            self._ls_func = ls_func
            self._try_create_bucket()

        def _try_create_bucket(self) -> Self:
            try:
                self.bucket.create()
            except Exception as e:
                Settings.LOGGER.warning(f"Failed to create bucket {self.bucket_name}: {e}")

            return self

        def cb(self, bucket: str) -> Self:
            """Return a new S3Driver with a different bucket. If it doesn't exist,
            the driver will attempt to create it

            :param bucket: The bucket name
            :type bucket: str
            :returns: A new S3Driver (the current is not modified)
            :rtype: S3Driver
            """
            result = S3Driver.__new__()
            result.resource = self.resource
            result.bucket = result.resource.Bucket(bucket)
            result.bucket_name = bucket
            result._ls_func = self._ls_func
            return result._try_create_bucket()

        def upload_file(self, src: Path|str, dst: Path|str) -> Path:
            """Upload a file from a local `src` path to a remote
            `dst` S3 key

            :param src: The path of the file
            :type src: Path|str
            :param dst: The destination key
            :type dst: Path|str
            :raises: FileNotFoundError, OSError, various boto3 errors
            :returns: The destination key
            :rtype: Path
            """
            self.bucket.upload_file(str(src), str(dst))
            return dst

        def download_file(self, src: Path|str, dst: Path|str) -> Path:
            """Download a file from a remote `src` S3 key to a local `dst` path

            :param src: The source key
            :type src: Path|str
            :param dst: The path of the destination file
            :type dst: Path|str
            :raises: FileNotFoundError, OSError, various boto3 errors
            :returns: The destination file path
            :rtype: Path
            """
            Path(dst).parent.mkdir(parents = True, exist_ok = True)
            self.bucket.download_fileobj(str(src), Path(dst).open("wb"))
            return dst

        def upload(self, src: PathSpec, dst: PathSpec) -> PathSpec:
            """Wraps :func:`eo4eu_data_utils.stream.S3Driver.upload_file`
            for use within streams. Instead of paths/strings, it uses PathSpec
            objects.


            :param src: The path of the file
            :type src: PathSpec
            :param dst: The destination key
            :type dst: PathSpec
            :raises: FileNotFoundError, OSError, various boto3 errors
            :returns: `dst` without modifying it
            :rtype: PathSpec
            """
            self.upload_file(src.path, dst.path)
            return dst

        def download(self, src: PathSpec, dst: PathSpec) -> PathSpec:
            """Wraps :func:`eo4eu_data_utils.stream.S3Driver.download_file`
            for use within streams. Instead of paths/strings, it uses PathSpec
            objects.

            :param src: The source key
            :type src: PathSpec
            :param dst: The path of the destination file
            :type dst: PathSpec
            :raises: FileNotFoundError, OSError, various boto3 errors
            :returns: `dst` without modifying it
            :rtype: PathSpec
            """
            self.download_file(src.path, dst.path)
            return dst

        def ls(self, src: Path|str) -> List[PathSpec]:
            """Calls :class:`eo4eu_data_utils.stream.S3Driver.list_objects`
            and passes it to this instance's `ls_func`

            :param src: The S3 prefix to list for objects
            :type src: Path|str
            :raises: various boto3 errors, whatever `ls_func` may raise
            :returns: A list of PathSpecs representing the objects found in the prefix
            :rtype: List[PathSpec]
            """
            return [
                self._ls_func(summary, src)
                for summary in self.list_objects(src)
            ]

        def list_objects(self, input_path: Path|str = "") -> List[Any]:
            """List the objects in the bucket which have the specified prefix

            :params input_path: The prefix the objects must have
            :type input_path: Path|str
            :raises: various boto3 errors
            :returns: The summaries of all objects matching the prefix
            :rtype: List[S3.ServiceResource.ObjectSummary]
            """
            input_path_str = str(input_path)
            if input_path_str == ".":
                input_path_str = ""
            elif input_path_str.startswith("./"):
                input_path_str = input_path_str[2:]

            return [
                summary
                for summary in self.bucket.objects.filter(Prefix = input_path_str)
                if summary.key != input_path_str and summary.key != f"{input_path_str}/"
            ]

        def upload_bytes(self, key: str|Path, data: bytes):
            """Upload an in-memory chunk of data to a remote `dst` S3 key

            :param key: The destination key
            :type key: Path|str
            :param data: The bytes of data
            :type data: bytes
            :raises: various boto3 errors
            """
            self.bucket.put_object(Key = str(key), Body = data)

        def download_bytes(self, key: str|Path) -> bytes:
            """Download an object from a remote `src` S3 key and return
            its contents as bytes

            :param key: The source key
            :type key: Path|str
            :raises: various boto3 errors
            :returns: The object bytes
            :rtype: bytes
            """
            return self.resource.Object(self.bucket_name, str(key)).get()["Body"].read()


    def get_last_modified_s3_prefix(s3_driver: S3Driver) -> str:
        """Returns the last modified prefix in the S3 driver's bucket. Prefix here
        means everything before the first ``"/"`` character.

        :param s3_driver: An S3 driver pointed to the bucket in question
        :type s3_driver: S3Driver
        :raises: ValueError, various boto3 errors
        :rtype: str
        """
        objects = s3_driver.bucket.objects.filter()
        sorted_objects = sorted(objects, key = lambda obj: obj.last_modified, reverse = True)
        if len(sorted_objects) <= 0:
            raise ValueError("No objects found")

        last_modified_prefix = ""  # if no subfolders are found, list top level
        for obj in sorted_objects:
            obj_parts = Path(obj.key).parts
            if len(obj_parts) > 1:
                last_modified_prefix = obj_parts[0]
                break

        return last_modified_prefix


    def list_last_modified_s3_prefix(s3_driver: S3Driver) -> List[str]:
        """List all the keys having the last modified prefix in the
        S3 driver's bucket.

        :param s3_driver: An S3 driver pointed to the bucket in question
        :type s3_driver: S3Driver
        :raises: ValueError, various boto3 errors
        :return: All keys which start with the last modified prefix
        :rtype: List[str]
        """
        last_modified_prefix = get_last_modified_s3_prefix(s3_driver)
        return [
            summary.key for summary in s3_driver.list_objects(last_modified_prefix)
        ]
else:
    S3Driver = _s3_module.broken_class("S3Driver")
    get_last_modified_s3_prefix = _s3_module.broken_func("get_last_modified_s3_prefix")
    list_last_modified_s3_prefix = _s3_module.broken_func("list_last_modified_s3_prefix")

    err_msg = "Something went wrong during the building of this documentation"
    S3Driver.__doc__ = err_msg
    get_last_modified_s3_prefix.__doc__ = err_msg
    list_last_modified_s3_prefix.__doc__ = err_msg


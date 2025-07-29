import shutil
from pathlib import Path
from zipfile import ZipFile, is_zipfile
from abc import ABC, abstractmethod
from eo4eu_base_utils import if_none
from eo4eu_base_utils.typing import Callable, Iterator, List


def unsafe_unpack(src: Path, dst: Path, **kwargs) -> List[Path]:
    """Try and unpack the archive file in ``src`` into the ``dst``
    directory. This function does not protect against zip bombs!

    :param src: The path to the input archive file
    :type src: Path
    :param dst: The path to the output directory
    :type dst: Path
    :param kwargs: Ignored
    :raises: ValueError if ``dst`` is not a directory, FileNotFoundError, OSError, various unpack errors
    :returns: A list containing the paths of all unpacked files
    :rtype: List[Path]
    """
    dst.mkdir(parents = True, exist_ok = True)
    if not dst.is_dir():
        raise ValueError(f"Unpack destination \"{dst}\" is not a directory")

    if src.suffix == ".zip":
        with ZipFile(src, "r") as archive:
            archive.extractall(dst)
    else:
        shutil.unpack_archive(src, dst)

    return [
        path for path in dst.rglob("*")
        if path.is_file()
    ]
# 
# 
# class Reader(ABC):
#     @abstractmethod
#     def read(self, size: int = -1) -> bytes:
#         return b""
# 
# 
# class ArchiveItem(ABC):
#     @abstractmethod
#     def read(self, size: int = -1) -> bytes:
#         return b""
# 
# 
# class ArchiveMapper(ABC):
#     @abstractmethod
#     def map(self, func: Callable[[ArchiveItem],Path], *args, **kwargs):
#         pass
# 
# 
# class ZipMapper(ArchiveMapper):
#     def __init__(
#         self,
#         path: str|Path,
#         filename_filter: Callable[[str],bool]|None = None,
#         ignore_dirs: bool = True,
#         kwargs: dict|None = None,
#     ):
#         self._path = path
#         self._filename_filter = if_none(filename_filter, lambda name: True)
#         self._ignore_dirs = ignore_dirs
#         self._kwargs = if_none(kwargs, {})
# 
#     def map(self, func: Callable[[ArchiveItem,Path],Path], *args, **kwargs):
#         if not is_zipfile(self._path):
#             raise ValueError(f"Path \"{self._path}\" is not a valid zip file.")
# 
#         with ZipFile.open(self._path, "r") as archive:
#             for item in archive.infolist():
#                 if item.is_dir() and self._ignore_dirs:
#                     continue
#                 if not self._filename_filter(item.filename):
#                     continue
# 
#                 with archive.open(item, "r") as reader:
#                     try:
#                         func(reader, *args, **kwargs)
#                     except Exception as e:
#                         help_logger.warning(f"Failed to unpack item \"{item.filename}\": {e}")
# 
# 
# def _safe_unpack_single(
#     reader: ArchiveItem,
#     dst: Path,
#     chunk_size: int = 10240,
#     max_file_size: int = 1e9,
#     filename_filter: Callable[[str],bool]|None = None,
# ) -> int:
#     max_iter = int(max_file_size / chunk_size) + 1
#     total_bytes_written = 0
# 
#     with dst.open("wb") as dst_file:
#         for _ in max_iter:
#             data = reader.read(chunk_size)
#             total_bytes_written += dst_file.write(data)
#             if len(data) < chunk_size:
#                 return total_bytes_written
# 
#     dst.unlink()
#     raise ValueError(f"Unpacked file exceeded max size of {max_file_size} bytes")
# 
# 
# def safe_unpack(
#     src: Path,
#     dst: Path,
#     max_total_size: int = 50e9,
#     zip_kwargs: dict|None = None,
#     tar_kwargs: dict|None = None,
#     **map_kwargs
# ):
#     filename_filter = if_none(filename_filter, lambda name: True)
#     zip_kwargs = if_none(zip_kwargs, {})
#     tar_kwargs = if_none(tar_kwargs, {})
# 
#     dst.mkdir(parents = True, exist_ok = True)
#     if not dst.is_dir():
#         raise ValueError(f"Unpack destination \"{dst}\" is not a directory")
# 
#     mapper = None
#     if src.suffix == ".zip":
#         mapper = ZipMapper(**zip_kwargs)
#     else:
#         raise ValueError(f"Unknown archive file extension for \"{src}\"")
# 
#     mapper.map(_safe_unpack_single, dst, **map_kwargs)

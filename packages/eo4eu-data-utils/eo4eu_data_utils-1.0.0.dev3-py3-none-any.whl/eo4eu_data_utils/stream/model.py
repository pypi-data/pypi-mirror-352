from pathlib import Path
from abc import ABC, abstractmethod
from eo4eu_base_utils import if_none
from eo4eu_base_utils.unify import overlay
from eo4eu_base_utils.typing import Self, Any, List, Dict, Iterator

from ..settings import Settings


class PathSpec:
    """An object representing a file. It separates between
    the file's path and its name. The former is used to access
    the contents of the file by the code in this submodule, while
    the latter informs the code how to name results of operations
    on this file. It can also hold metainfo pertaining to the file.

    :param name: The name of the file
    :type name: str|Path
    :param path: The full path of the file
    :type path: str|Path
    :param meta: Metainfo dictionary for this file
    :type meta: Dict[str,Any]|None
    """

    __slots__ = ("name", "path", "meta")

    def __init__(self, name: Path, path: Path, meta: Dict[str,Any]|None = None):
        self.name = Path(name)
        """The name of the file"""
        self.path = Path(path)
        """The path of the file"""
        if meta is None:
            meta = {}
        self.meta = meta
        """The metainfo of the file"""

    def but(self, **kwargs) -> Self:
        """Create a new PathSpec, substituting the given arguments

        :param kwargs: Only valid keywords are \"name\", \"path\" and \"meta\", as they are passed to a new PathSpec constructor. Where they are not given, this instance's values are used. Warning: The PathSpec's metainfo dictionary is only shallowly copied!
        :type kwargs: Dict[str,Any]
        :returns: A new PathSpec (the original is not modified!)
        :rtype: PathSpec
        """
        return PathSpec(**({
            "name": self.name,
            "path": self.path,
            "meta": self.meta.copy(),
        } | kwargs))

    def __getitem__(self, name: str) -> Any:
        return self.meta[name]

    def __setitem__(self, name: str, val: Any):
        self.meta[name] = val

    def __repr__(self) -> str:
        return Settings.PATHSPEC_FORMATTER(self.name, self.path, self.meta)


class Data:
    """A container holding a sequence of objects. Actually,
    it holds two sequences: ``Data.passed`` and ``Data.failed``.
    These represent operations which have either succeeded or
    failed in previous stages of a data processing pipeline. Typically,
    an operation will act on the passed objects and maybe log
    the failed ones, warning the user.

    :param passed: The objects which have made it through previous stages successfully
    :type passed: List[Any]
    :param failed: The objects for which there were errors in previous stages
    :type failed: List[Any]
    :param kwargs: Options global to the objects being processed
    :type kwargs: Dict[str,Any]
    """

    __slots__ = ("passed", "failed", "kwargs")

    def __init__(
        self,
        passed: List[Any]|None = None,
        failed: List[Any]|None = None,
        kwargs: Dict[str,Any]|None = None
    ):
        self.passed = if_none(passed, [])
        """The objects which have made it through previous stages successfully"""
        self.failed = if_none(failed, [])
        """The objects for which there were errors in previous stages"""
        self.kwargs = if_none(kwargs, {})
        """Options global to the objects being processed"""

    @classmethod
    def empty(self) -> Self:
        """Construct a Data object with no objects and no metadata

        :rtype: Data
        """
        return Data([], [], {})

    def but(self, **kwargs) -> Self:
        """Create a new Data object, substituting the given arguments

        :param kwargs: Only valid keywords are \"passed\", \"failed\" and \"kwargs\", as they are passed to a new Data constructor. Where they are not given, this instance's values are used. Warning: The Data's metainfo dictionary is only shallowly copied!
        :type kwargs: Dict[str,Any]
        :returns: A new Data object (the original is not modified!)
        :rtype: Data
        """
        return Data(**({
            "passed": self.passed,
            "failed": self.failed,
            "kwargs": self.kwargs.copy(),
        } | kwargs))

    def __iter__(self) -> Iterator[Any]:
        for item in self.passed:
            yield item

    def iter_all(self) -> Iterator[Any]:
        """Iterate through both self.passed and self.failed

        :rtype: Iterator[Any]
        """
        for passed in self.passed:
            yield passed
        for failed in self.failed:
            yield failed

    def merge(self, other: Self) -> Self:
        """Merge two Data objects. The result is a new Data object
        created by concatenating the passed and failed from self
        and other, and calling :func:`eo4eu_base_utils.unify.overlay`
        on their metainfo dictionaries.

        :param other: Another Data object
        :type other: Data
        :returns: A new Data object (the original is not modified!)
        :rtype: Data
        """
        return Data(
            passed = self.passed + other.passed,
            failed = self.failed + other.failed,
            kwargs = overlay(self.kwargs, other.kwargs)
        )

    def len(self) -> int:
        """The length of self.passed

        :rtype: int
        """
        return len(self.passed)

    def stats(self) -> tuple[int,int]:
        """A tuple containing the length of self.passed and that
        of self.failed

        :rtype: tuple[int,int]
        """
        return (len(self.passed), len(self.failed))

    def warn_stats(self) -> tuple[int,int]:
        """A tuple containing the length of self.passed and the sum of
        it with the length of self.failed (total)

        :rtype: tuple[int,int]
        """
        return (len(self.failed), len(self.passed) + len(self.failed))

    def any_failed(self) -> bool:
        """Returns False if self.failed is empty, True otherwise

        :rtype: bool
        """
        return len(self.failed) > 0

    def __repr__(self) -> str:
        return Settings.DATA_FORMATTER(
            self.passed, self.failed, self.kwargs
        )


class Downloader(ABC):
    """An interface for objects which download files"""

    @abstractmethod
    def download(self, src: PathSpec, dst: PathSpec) -> PathSpec:
        """Download src into dst"""
        pass


class Uploader(ABC):
    """An interface for objects which upload files"""

    @abstractmethod
    def upload(self, src: PathSpec, dst: PathSpec) -> PathSpec:
        """Upload src into dst"""
        pass


class Lister(ABC):
    """An interface for objects that can \"list\" \"directories\""""

    @abstractmethod
    def ls(self, src: Path) -> List[PathSpec]:
        """List the directory src"""
        return []


class Action(ABC):
    """An interface for objects that can act on Data objects"""

    @abstractmethod
    def act(self, input: Data) -> Data:
        """Transform Data objects in some way"""
        return input

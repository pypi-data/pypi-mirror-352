import os
from pathlib import Path
from pprint import pformat
from abc import ABC, abstractmethod
from eo4eu_base_utils.typing import Any
from eo4eu_base_utils.result import Result

from .model import Source
from .utils import _get_all_keys


class FileSource(Source):
    """This class looks for local files in the provided path.

    :param root: The working directory to look from. Default is system root.
    :type root: str|Path
    """

    def __init__(self, root: str|Path = "/"):
        self.root = Path(root)
        self._cache = {}

    def get(self, args: list[str|Path]) -> Result:
        """Read the file specified by joining all members in `args`.

        :param args: The path parts
        :type args: List[str|Path]
        :returns: Either a Result.ok wrapping the contents of a file or a Result.err
        :rtype: eo4eu_base_utils.result.Result
        """
        if len(args) == 0:
            return Result.err("No file path provided.")

        path = self.root.joinpath(*args)
        path_str = str(path)
        try:
            if path_str not in self._cache:
                self._cache[path_str] = path.read_text()

            return Result.ok(self._cache[path_str])
        except Exception as e:
            return Result.err(f"Could not read from \"{path_str}\": {e}")


class DictSource(Source):
    """This class looks for nested keys in a Python dict.

    :param content: The Python dict containing the data
    :type content: Dict
    :param arg_kind: The name of the arguments used for logging messages (for example, \"Could not find <arg_kind> some.nested.key: ...\")
    :type arg_kind: str
    """

    def __init__(self, content: dict, arg_kind: str = "dict key"):
        self.content = content
        self.arg_kind = arg_kind

    def get(self, args: list[str]) -> Result:
        """Get nested key from dictionary.

        :param args: The nested keys
        :type args: List[str]
        :returns: A Result.ok wrapping the nested value, or Result.err if it doesn't exist
        :rtype: eo4eu_base_utils.result.Result
        """
        if len(args) == 0:
            return Result.err(f"No {self.arg_kind}(s) provided.")

        try:
            result = self.content.copy()
            for arg in args:
                result = result[arg]

            return Result.ok(result)
        except Exception as e:
            key_str = ".".join([str(arg) for arg in args])
            return Result.err(
                f"Could not find {self.arg_kind} \"{key_str}\" in {pformat(_get_all_keys(self.content))}"
            )


class EnvSource(Source):
    """This class looks to environment variables for data."""

    def __init__(self):
        pass

    def get(self, args: list[str]) -> Result:
        """Get environment variable defined by `args` This is done
        by converting all alphabetical characters to uppercase, replacing
        all '-' with '_', and joining the arguments with '_'. For example,
        calling EnvSource.get on [\"some\", \"env\", \"var\"] will try
        to find SOME_ENV_VAR

        :param args: The path that defines the given environment variable
        :type args: list[str]
        :returns: A Result.ok wrapping the value of the environment variable, or Result.err if it doesn't exist
        :rtype: eo4eu_base_utils.result.Result
        """
        key = "_".join([arg.replace("-", "_").upper() for arg in args])
        try:
            return Result.ok(os.environ[key])
        except Exception as e:
            return Result.err(f"Could not find environment variable: {key}")


class CompoundSource(Source):
    """A source which looks through a list of sources and
    returns the first successful result.

    :param sources: A list of other sources
    :type source: List[Source]"""

    def __init__(self, sources: list[Source]):
        self.sources = sources

    def get(self, args: list) -> Result:
        """Look for the data in this instance's sources, returning the
        first Result.ok, or Result.err if all sources returned an error.

        :param args: The path to look at
        :type args: List
        :rtype: eo4eu_base_utils.result.Result
        """
        result = Result.none()
        for source in self.sources:
            result = result.then(source.get(args))
            if result.is_ok():
                return result
        return result

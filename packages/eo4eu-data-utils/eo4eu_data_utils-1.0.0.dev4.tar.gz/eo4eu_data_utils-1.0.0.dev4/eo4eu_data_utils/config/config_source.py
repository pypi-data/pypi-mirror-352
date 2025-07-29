import os
import re
from pathlib import Path
from abc import ABC, abstractmethod
from eo4eu_base_utils.typing import List, Dict, Any, Callable, Self


def _format_keys(keys: List[Any], sep: str = "."):
    return sep.join([str(key) for key in keys])


class SourceError(Exception):
    """A generic exception to be raised whenever a
    value cannot be sourced.
    """
    pass


class SimpleSource(ABC):
    """An interface similar to :class:`eo4eu_data_utils.config.source.Source`,
    but instead of using :class:`eo4eu_base_utils.result.Result` it is
    supposed to raise an exception if it can't find the requested data.
    """

    @abstractmethod
    def get(self, keys: List[Any]) -> Any:
        """Get the requested data/nested key

        :param keys: The filesystem path parts
        :type keys: List[str|Path]
        """
        return None


class SimpleFileSource(SimpleSource):
    """A SimpleSource that reads from files.

    :param root: The filesystem root from which to evaluate paths
    :type root: str|Path
    :param reader: The function to run when reading from files. (default: Path.read_text)
    :type reader: Callable[[Path],Any]|None
    """

    def __init__(
        self,
        root: str|Path = "/",
        reader: Callable[[Path],Any]|None = None
    ):
        if reader is None:
            reader = lambda path: path.read_text()

        self._root = Path(root)
        self._reader = reader

    def get(self, keys: List[Any]) -> Any:
        """Read the contents of the path specified by
        joining the parts in `keys`

        :param keys: The filesystem path parts
        :type keys: List[str|Path]
        :raises: FileNotFoundError, whatever `reader` raises
        :rtype: Whatever `reader` returns (default: str)
        """
        path = self._root.joinpath(*keys)
        return self._reader(path)


class SimpleDictSource(SimpleSource):
    """A SimpleSource that reads from a python dictionary

    :param data: The dictionary to use as a source
    :type data: Dict
    """

    def __init__(self, data: Dict):
        self._data = data

    def get(self, keys: List[Any]) -> Any:
        """Read the contents of the given nested key

        :param keys: The nested key
        :type keys: List[str|Path]
        :raises: KeyError
        :rtype: Any
        """
        result = self._data
        for key in keys:
            result = result[key]

        return result


class SimpleEnvSource(SimpleSource):
    """A SimpleSource that reads from the program's environment

    :param converter: The function that converts a nested key list to an environment variable name. By default, it drops non-alphanimeric characters, converts \"-\" to \"_\", converts to uppercase, and joins all parts with \"_\". For example, ``[\"some\", \"e!nv\", \"var-na@me\"]`` will be converted to ``\"SOME_ENV_VAR_NAME\"``.
    :type converter: Callable[[List[Any]],str]|None
    """

    def __init__(self, converter: Callable[[List[Any]],str]|None = None):
        non_alphanum_re = re.compile("[^a-zA-Z0-9_]")
        if converter is None:
            converter = lambda keys: "_".join([
                non_alphanum_re.sub("", str(key).replace("-", "_")).upper()
                for key in keys
            ])

        self._converter = converter

    def get(self, keys: List[Any]) -> Any:
        """Read the contents of the given environment variable

        :param keys: The nested key that will be converted to an environment variable name
        :type keys: List[str|Path]
        :raises: :class:`eo4eu_data_utils.config.config_source.SourceError`
        :rtype: str
        """
        env_var = self._converter(keys)
        if env_var in os.environ:
            return os.environ[env_var]
        else:
            raise SourceError(f"Failed to find environment variable \"{env_var}\"")


# This class is a procedural alternative to the declarative
# "ConfigBuilder" class; it is much simpler
class ConfigSource:
    """This class is a simpler alternative to
    :class:`eo4eu_data_utils.config.ConfigBuilder`. Where
    ConfigBuilder is meant to be declarative, this is fully
    imperative. In essence, it acts like a dictionary that
    tries many ways of finding requested values.

    :param sources: The sources to look at for values
    :type sources: List[SimpleSource]|None
    """

    def __init__(self, sources: List[SimpleSource]|None = None):
        if sources is None:
            sources = []

        self._sources = sources

    def get(
        self,
        *keys: Any,
        apply: Callable[[Any],Any]|None = None
    ) -> Any:
        """Get the nested keys from one of the sources

        :param keys: The item path/nested keys to fetch the value of
        :type keys: tuple[Any]
        :raises: :class:`eo4eu_data_utils.config.config_source.SourceError`
        :returns: The result of the keys from the first source that doesn't raise an exception
        :rtype: Any
        """
        if apply is None:
            apply = lambda x: x

        errors = []
        for source in self._sources:
            try:
                return apply(source.get(keys))
            except Exception as e:
                errors.append(str(e))

        error_blurb = "\n\t".join(errors)
        raise SourceError(
            f"Failed to get \"{_format_keys(keys)}\":\n\t{error_blurb}"
        )

    def try_get(
        self,
        *keys: Any,
        default: Any = None,
        **kwargs
    ) -> Any:
        """Get the nested keys from one of the sources. If the data is not found,
        return some default value.


        :param keys: The item path/nested keys to fetch the value of
        :type keys: tuple[Any]
        :param default: The default value to be returned when the data is not found in any of the sources
        :type default: Any
        :param kwargs: Keyword arguments passed to :func:`ConfigSource.get`
        :type kwargs: Dict
        :returns: The result of the keys from the first source that doesn't raise an exception, otherwise `default`
        :rtype: Any
        """
        if "default" in kwargs:
            default = kwargs["default"]
            del kwargs["default"]

        try:
            return self.get(*keys, **kwargs)
        except Exception:
            return default

    def use(self, source: SimpleSource) -> Self:
        """Add this :class:`eo4eu_data_utils.config.config_source.SimpleSource` to the list of sources available to this `ConfigSource`

        :param source: A data source
        :type source: SimpleSource
        :returns: Itself (the ConfigSource is modified inplace!)
        :rtype: ConfigSource
        """
        self._sources.append(source)
        return self

    def use_files(self, *args, **kwargs) -> Self:
        """Adds a :class:`eo4eu_data_utils.config.config_source.SimpleFileSource`
        to this ConfigSource

        :param args: The positional arguments passed to the SimpleFileSource constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments passed to the SimpleFileSource constructor
        :type kwargs: Dict[Any]
        :returns: Itself (the ConfigSource is modified inplace!)
        :rtype: ConfigSource
        """
        return self.use(SimpleFileSource(*args, **kwargs))

    def use_dict(self, *args, **kwargs) -> Self:
        """Adds a :class:`eo4eu_data_utils.config.config_source.SimpleDictSource`
        to this ConfigSource

        :param args: The positional arguments passed to the SimpleDictSource constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments passed to the SimpleDictSource constructor
        :type kwargs: Dict[Any]
        :returns: Itself (the ConfigSource is modified inplace!)
        :rtype: ConfigSource
        """
        return self.use(SimpleDictSource(*args, **kwargs))

    def use_env(self, *args, **kwargs) -> Self:
        """Adds a :class:`eo4eu_data_utils.config.config_source.SimpleEnvSource`
        to this ConfigSource

        :param args: The positional arguments passed to the SimpleEnvSource constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments passed to the SimpleEnvSource constructor
        :type kwargs: Dict[Any]
        :returns: Itself (the ConfigSource is modified inplace!)
        :rtype: ConfigSource
        """
        return self.use(SimpleEnvSource(*args, **kwargs))

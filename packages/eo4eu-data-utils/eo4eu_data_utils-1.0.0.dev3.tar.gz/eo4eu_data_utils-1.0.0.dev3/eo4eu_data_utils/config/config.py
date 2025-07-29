import json
import logging
from pathlib import Path
from pprint import pformat
from eo4eu_base_utils.result import Result
from eo4eu_base_utils.typing import Self, Iterator, Any, Dict

from .utils import _get_nested, _get_all_keys
from .model import Filler, Source
from .source import (
    EnvSource,
    DictSource,
    FileSource,
    CompoundSource,
)

from ..settings import Settings


class ConfigError(Exception):
    """A generic exception to be raised whenever a
    configuration cannot be built.
    """
    pass


class Config:
    """This class is, essentially, a wrapper around a `Dict`.
    You can access its values using [\"name\"] or .name (attribute-like access)


    :param attrs: The attributes as a dictionary. Nested dictionaries will be converted to nested `Config` objects
    :type attrs: Dict|None
    """
    def __init__(self, attrs: Dict|None = None):
        if attrs is None:
            attrs = {}

        self._attrs = {
            key: (Config(val) if isinstance(val, dict) else val)
            for key, val in attrs.items()
            if key[0] != "_"
        }

    def to_dict(self) -> Dict:
        """Converts the `Config` object to a regular Python dictionary

        :rtype: Dict
        """
        return {
            key: val.to_dict() if isinstance(val, self.__class__) else val
            for key, val in self.items()
        }

    def to_json(self) -> str:
        """Converts the `Config` object to a Python dict and serializes it
        to JSON

        :rtype: str
        """
        return json.dumps(self.to_dict())

    def __getattr__(self, key: str):
        if key[0] == "_":
            return super().__getattr__(key)
        return self._attrs[key]

    def __setattr__(self, key: str, val):
        if key[0] == "_":
            return super().__setattr__(key, val)
        self._attrs[key] = val

    def __getitem__(self, key: str):
        return self._attrs[key]

    def __setitem__(self, key: str, val):
        self._attrs[key] = val

    def __repr__(self) -> str:
        return pformat(self.to_dict())

    def items(self) -> Iterator[tuple[str,Any]]:
        """Same as Dict.items

        :rtype: Iterator[tuple[str,Any]]
        """
        return self._attrs.items()

    def get(self, value: str, default: Any = None) -> Any:
        """Same as Dict.get

        :param value: The name of the value to fetch
        :type value: str
        :param default: The default value to return if `value` is not in the `Config` object
        :type default: Any
        :rtype: Any
        """
        if value in self._attrs:
            return self._attrs[value]
        return default


class ConfigBuilder(Filler, Source):
    """This is a class for generating :class:`eo4eu_data_utils.config.Config`
    objects from various sources

    :param kwargs: May hold dictionaries, instances of Filler, or arbitrary objects
    :type kwargs: Dict[str,Any]
    """
    def __init__(self, **kwargs):
        self._logger = kwargs.get("_logger", Settings.LOGGER)
        self._root = kwargs.get("_root", self)
        self._sources = []
        self._source = None
        self._attrs = {
            key: ConfigBuilder(
                **val,
                _logger = self._logger,
                _root = self._root
            ) if isinstance(val, dict) else val
            for key, val in kwargs.items()
            if key[0] != "_"
        }

    @classmethod
    def from_dict(cls, items: Dict) -> Self:
        """Alternative constructor, equivalent to ConfigBuilder(\*\*items)

        :param items: The dictionary holding the keyword arguments
        :type items: Dict[str,Any]
        :rtype: ConfigBuilder
        """
        return ConfigBuilder(**items)

    @classmethod
    def from_json(cls, items: str) -> Self:
        """Alternative constructor which deserializes JSON

        :param items: The JSON string holding the keyword arguments
        :type items: str
        :rtype: ConfigBuilder
        """
        return cls.from_dict(json.loads(items))

    def __getitem__(self, key: str):
        return self._attrs[key]

    def __setitem__(self, key: str, val):
        self._attrs[key] = val

    def items(self) -> Iterator[tuple[str,Any]]:
        """Same as Dict.items

        :rtype: Iterator[tuple[str,Any]]
        """
        return self._attrs.items()

    def __repr__(self) -> str:
        return pformat(self.to_dict())

    def _fmt_all_keys(self) -> str:
        return pformat(_get_all_keys(self._root))

    def inherit(self, root: Self, logger: logging.Logger) -> Self:
        """Get attributes from another ConfigBuilder

        :param root: The root ConfigBuilder
        :type root: ConfigBuilder
        :param logger: The logger to use for messages
        :type logger: logging.Logger
        :rtype: ConfigBuilder
        """
        self._root = root
        self._logger = logger
        return self

    def set_source(self, source: Source) -> Self:
        """Set the current source

        :param source: The source to use
        :type source: Source
        :rtype: ConfigBuilder
        """
        self._source = source
        return self

    def use_source(self, source: Source) -> Self:
        """Append this source to the list of sources to be used

        :param source: The source to add
        :type source: Source
        :rtype: ConfigBuilder
        """
        self._sources.append(source)
        self._source = CompoundSource(self._sources)
        return self

    def use_files(self, root: str|Path = "/") -> Self:
        """Append a :class:`eo4eu_data_utils.config.source.FileSource` to
        the list of sources to be used

        :param root: The root directory of the FileSource
        :type root: str|Path
        :rtype: ConfigBuilder
        """
        return self.use_source(FileSource(root))

    def use_env(self) -> Self:
        """Append a :class:`eo4eu_data_utils.config.source.EnvSource` to
        the list of sources to be used

        :rtype: ConfigBuilder
        """
        return self.use_source(EnvSource())

    def use_dict(self, source: dict, **kwargs) -> Self:
        """Append a :class:`eo4eu_data_utils.config.source.DictSource` to
        the list of sources to be used

        :param source: The underlying dictionary
        :type source: Dict
        :param kwargs: Keyword arguments passed to the DictSource constructor
        :type kwargs: Dict
        :rtype: ConfigBuilder
        """
        return self.use_source(DictSource(source, **kwargs))

    def use_json(self, source: str, **kwargs) -> Self:
        """Append a :class:`eo4eu_data_utils.config.source.DictSource` created
        by deserializing a JSON string to the list of sources to be used

        :param source: The underlying JSON data
        :type source: str
        :param kwargs: Keyword arguments passed to the DictSource constructor
        :type kwargs: Dict
        :rtype: ConfigBuilder
        """
        return self.use_dict(json.loads(source), **kwargs)

    def get(self, args: list[str]) -> Result:
        """This makes sure :class:`eo4eu_data_utils.config.ConfigBuilder`
        fulfills the :class:`eo4eu_data_utils.config.model.Source` interface.
        Looks into the instance's added sources. If the first argument is ``"__parent"``
        it will try looking at the root ConfigBuilder for the appropriate keys.
        If the value found is a :class:`eo4eu_data_utils.config.model.Filler`,
        the ConfigBuilder will attempt to use its ``fill()`` method to get a 
        result.

        :params args: The path/nested key to search for
        :type args: List[str]
        :returns: Result.ok(value) if the nested key value is found, otherwise Result.err
        :rtype: eo4eu_base_utils.result.Result
        """
        if len(args) == 0:
            return Result.err(f"No keys provided")

        head, tail = args[0], args[1:]
        if head != "__parent":
            return self._source.get(args)
        try:
            result = _get_nested(self._root, tail)
            if isinstance(result, Filler):
                return result.fill(self._root, Result.none())
            else:
                return Result.ok(result)
        except Exception as e:
            return Result.err(
                f"Could not find config key \"{'.'.join(tail)}\" in {self._fmt_all_keys()}: {e}"
            )

    def fill(self, source: Source, val: Result) -> Result:
        """This makes sure :class:`eo4eu_data_utils.config.ConfigBuilder`
        fulfills the :class:`eo4eu_data_utils.config.model.Filler` interface.
        Loops over its own keys. If the key is a Filler, it tries
        calling its ``fill()`` method using **itself** as a source
        (ConfigBuilder objects are both sources and fillers!!!) and
        returning the output. Otherwise, the value is kept as-is.
        In the end, a :class:`eo4eu_data_utils.config.Config` object
        is constructed holding all the proper values.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        previous_keys = val.get_or([])
        result = Config()
        for key, val in self.items():
            keys = previous_keys + [key]
            filled_val = Result.ok(val)

            if isinstance(val, self.__class__):
                val.set_source(self._source)
                filled_val = val.fill(self, Result.ok(keys))
            elif isinstance(val, Filler):
                filled_val = val.fill(self, Result.none())

            if filled_val.is_ok():
                result[key] = filled_val.get()
            else:
                return filled_val.then_err(f"Failed to fill config key \"{'/'.join(keys)}\"")

        return Result.ok(result)

    def build(self, clear_sources: bool = True) -> Config:
        """A convenience wrapper around :func:`ConfigBuilder.fill`.
        It returns a :class:`eo4eu_data_utils.config.Config` and
        raises a :class:`eo4eu_data_utils.config.ConfigError`
        if the configuration cannot be filled.

        :param clear_sources: If True, removes the added sources after building the Config object (default: True)
        :type clear_sources: bool
        :raises: :class:`eo4eu_data_utils.config.ConfigError`
        :rtype: Config
        """
        if self._source is None:
            raise ConfigError(f"Failed to build configuration: No sources set")

        result = self.fill(self, Result.none())
        if clear_sources:
            self._sources = []
            self._source = None

        if result.is_err():
            result.log(self._logger)
            raise ConfigError(f"Failed to build configuration")

        return result.get()

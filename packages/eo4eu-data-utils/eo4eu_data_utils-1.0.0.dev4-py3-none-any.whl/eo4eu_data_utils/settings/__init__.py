import logging
import functools
from pprint import pformat
from eo4eu_base_utils.typing import List, Dict, Any, Callable

from .safe_dict import SafeDict
from .data import (
    recover_soft_fail,
    recover_raise_exc,
    recover_continue,
)
from .format import (
    trim_root,
    shortest_unique,
    remove_duplicates,
    unique_sort_match,
    strict_distance,
    simple_distance,
    group_distance,
)

logger = logging.getLogger("eo4eu.data")
logger.setLevel(logging.INFO)


def _default_error_callback(item, exc, name, level):
    logger.log(
        level,
        f"Failed to {name} \"{item}\": {exc}"
    )

def _format_list(prefix: str, items: List[Any]) -> str:
    spaces = " " * len(prefix)
    if len(items) == 0:
        return f"{prefix}[]"
    if len(items) == 1:
        return f"{prefix}{items[0]}"

    head, tail = items[0], items[1:]
    return f"{prefix}{head}\n" + "\n".join([
        f"{spaces}{item}"
        for item in tail
    ])


class _DefaultPathspecFormatter:
    def __call__(self, name: str, path: str, meta: dict) -> str:
        try:
            name_is_in_path = path.match(name)
            if name_is_in_path:
                name_str = str(name)
                start = str(path)[::-1][len(name_str):][::-1]
                return f"{start}({name_str})"
            else:
                return f"{path}:({name})"
        except Exception as e:
            return f"[Failed to format path: {e}]"

    def __repr__(self) -> str:
        return "Callable[[str, str, str], str]"


class _DefaultDataFormatter:
    def __call__(self, passed: List[Any], failed: List[Any], kwargs: Dict) -> str:
        return "\n".join([
            _format_list("passed: ", passed),
            _format_list("failed: ", failed),
            f"kwargs: {pformat(kwargs)}",
        ])

    def __repr__(self) -> str:
        return "Callable[[List[Any], List[Any], Dict], str]"


class Settings:
    """Holds library-wide settings"""

    LOGGER = logger
    """The logger used by the library. By default, it's \"eo4eu.data\""""

    CFGMAP_PREFIX = "configmaps"
    """The prefix used for the :func:`eo4eu_data_utils.config.Try.cfgmap` constructor"""

    SECRET_PREFIX = "secrets"
    """The prefix used for the :func:`eo4eu_data_utils.config.Try.secret` constructor"""

    RENAME_METHODS = SafeDict({
        "trim_root":       trim_root,
        "shortest_unique": shortest_unique,
        "remove_duplicates": remove_duplicates,
    }, default = trim_root)
    """The methods available for renaming file paths. Entries:

    ``"trim_root"``: :func:`eo4eu_data_utils.settings.format.trim_root`

    ``"shortest_unique"``: :func:`eo4eu_data_utils.settings.format.shortest_unique`

    ``"remove_duplicates"``: :func:`eo4eu_data_utils.settings.format.remove_duplicates`

    Default is ``"trim_root"``.
    """

    FILL_META_METHODS = SafeDict({
        "unique_sort_match": unique_sort_match,
    }, default = unique_sort_match)
    """The methods available for filling metainfo from files. Entries:

    ``"unique_sort_match"``: :func:`eo4eu_data_utils.settings.format.unique_sort_match`

    Default is ``"unique_sort_match"``.
    """

    STRING_DISTANCE_METHODS = SafeDict({
        "strict_distance": strict_distance,
        "simple_distance": simple_distance,
        "group_distance":  group_distance,
    }, default = group_distance)
    """The methods available for measuring the \"distance\" of two strings. Entries:

    ``"strict_distance"``: :func:`eo4eu_data_utils.settings.format.strict_distance`

    ``"simple_distance"``: :func:`eo4eu_data_utils.settings.format.simple_distance`

    ``"group_distance"``: :func:`eo4eu_data_utils.settings.format.group_distance`

    Default is ``"group_distance"``.
    """

    RECOVERY_METHODS = SafeDict({
        "soft_fail": recover_soft_fail,
        "raise_exc": recover_raise_exc,
        "continue":  recover_continue,
    }, default = recover_soft_fail)
    """The methods available to streams for recovering from errors. Entries:

    ``"soft_fail"``: :func:`eo4eu_data_utils.settings.data.recover_soft_fail`

    ``"raise_exc"``: :func:`eo4eu_data_utils.settings.data.recover_raise_exc`

    ``"continue"``: :func:`eo4eu_data_utils.settings.data.recover_continue`

    Default is ``"recover_soft_fail"``.
    """

    PATHSPEC_FORMATTER = _DefaultPathspecFormatter()
    """The function to use for formatting :class:`eo4eu_data_utils.stream.PathSpec` objects"""

    DATA_FORMATTER = _DefaultDataFormatter()
    """The function to use for formatting :class:`eo4eu_data_utils.stream.Data` objects"""

    @classmethod
    def make_default_err_callback(cls, name: str, level: int = logging.WARNING) -> Callable[[Any,Exception],None]:
        """Create an callback function for logging errors
        (this is meant to be used internally)

        :param name: the name of the operation which produced the error
        :type name: str
        :param level: The logging level to log messages at (default: logging.WARNING)
        :type level: int
        :rtype: Callable[[Any,Exception],None]
        """
        return functools.partial(
            _default_error_callback,
            name = name,
            level = level
        )




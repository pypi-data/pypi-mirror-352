import functools
from eo4eu_base_utils.typing import Callable, Any, Dict, List

from ..settings import Settings


def _dict_like_predicate(item: Any, kwargs: Dict) -> bool:
    try:
        for key, val in kwargs.items():
            is_satisfied = False
            if callable(val):
                is_satisfied = val(item[key])
                if not isinstance(is_satisfied, bool):
                    is_satisfied = False
            elif isinstance(val, list) or isinstance(val, set):
                is_satisfied = item[key] in val
            else:
                is_satisfied = item[key] == val

            if not is_satisfied:  # all predicates must be true
                return False
        return True
    except Exception as e:
        Settings.LOGGER.warning(f"Failed to apply predicate to \"{item}\": {e}")
        return False


def select(**kwargs: List|set|Callable[[Any],bool]|Any) -> Callable[[Any],bool]:
    """Creates a predicate which selects dictionaries
    based on the keyword arguments passed. All keys must
    be valid in order for the dict to be valid.

    :param kwargs: Keyword arguments to validate. If the arg is a list/set, the value passes if it is in the list/set. If it is a callable, the value passes if the callable returns True. Otherwise, the value is directly compared to the argument.
    :type kwargs: Dict[str,List|set|Callable[[Any],bool]|Any]
    :rtype: Callable[[Any],bool]
    """
    return functools.partial(_dict_like_predicate, kwargs = kwargs)


def _dict_like_attach(item: Any, kwargs: Dict) -> Any:
    for key, val in kwargs.items():
        try:
            if callable(val):
                item[key] = val(item)
            else:
                item[key] = val
        except Exception as e:
            Settings.LOGGER.warning(f"Failed to attach \"{key}\" to \"{item}\": {e}")

    return item


def attach(**kwargs: Callable[[Dict],Any]|Any) -> Callable[[Any],Any]:
    """Creates a function which adds certain keys to
    dictionaries. Each keyword argument passed adds a
    value to the same key in the dictionary.

    :param kwargs: Keyword arguments to add/modify. If the arg is a callable, it will be called with the entire dictionary as the argument. Otherwise, the value of the key will be set to the arg.
    :type kwargs: Dict[str,Callable[[Dict],Any]|Any]
    :rtype: Callable[[Dict],Any]
    """
    return functools.partial(_dict_like_attach, kwargs = kwargs)

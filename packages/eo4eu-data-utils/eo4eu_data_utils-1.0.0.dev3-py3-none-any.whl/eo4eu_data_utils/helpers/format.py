from pathlib import Path
from eo4eu_base_utils import if_none
from eo4eu_base_utils.typing import List, Any

from ..settings import _format_list


def format_list(prefix: str, items: List[Any]) -> str:
    """Similar to :func:`pprint.pformat`, but will align all
    items in a list to match the prefix.

    :param prefix: A string to print before the list
    :type prefix: str
    :param items: A list of items
    :type items: List[Any]
    :rtype: str
    """
    return _format_list(prefix, items)

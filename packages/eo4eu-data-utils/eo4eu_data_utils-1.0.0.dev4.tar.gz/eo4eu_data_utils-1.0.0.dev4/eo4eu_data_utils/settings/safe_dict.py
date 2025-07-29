from eo4eu_base_utils.typing import Dict, Any, Self


class SafeDict:
    """A wrapper around a Python dictionary, which includes a
    default value that will always be returned if the requested key
    does not exist.

    :param attrs: The attributes of the safe dict
    :type attrs: Dict
    :param default: The default value
    :type default: Any
    """

    def __init__(self, attrs: Dict, default: Any):
        self._attrs = attrs
        self._default = default

    @classmethod
    def empty(cls) -> Self:
        """Returns an empty SafeDict, with the default value set to None

        :rtype: SafeDict
        """
        return SafeDict({}, None)

    def __getitem__(self, name: str) -> Any:
        """Same as dict.__getitem__"""
        return self._attrs.__getitem__(name)

    def __setitem__(self, name: str, value: Any) -> Any:
        """Same as dict.__setitem__"""
        return self._attrs.__setitem__(name, value)

    def union(self, other: Self) -> Self:
        """Return a new SafeDict, wrapping the result of the union
        between self.attrs and other.attrs and having other.default
        as the default value

        :param other: The other SafeDict
        :type other: SafeDict
        :rtype: SafeDict
        """
        return SafeDict(
            attrs = self._attrs | other._attrs,
            default = other._default
        )

    def get(self, name: str, default_key: str = None) -> Any:
        """Get the key from the dictionary. If it is not found,
        `default_key` is checked. If that is not found either,
        the SafeDict's default value is used.

        :param name: The key to search for
        :type name: str
        :param default_key: The key to check if `name` is not found
        :type default_key: str|None
        :rtype: Any
        """
        try:
            return self._attrs[name]
        except KeyError:
            if default_key is None:
                return self._default
            try:
                return self._attrs[default_key]
            except KeyError:
                return self._default

    def set_default(self, default: Any) -> Self:
        """Sets the SafeDict's default value

        :param default: The new default value
        :type default: Any
        :returns: The modified SafeDict (modification is done inplace!)
        :rtype: SafeDict
        """
        self._default = default
        return self

    def __repr__(self) -> str:
        return f"{self._attrs}, (default: {self._default})"

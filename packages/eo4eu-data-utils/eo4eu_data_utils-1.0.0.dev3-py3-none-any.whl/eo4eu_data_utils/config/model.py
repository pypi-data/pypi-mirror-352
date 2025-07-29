from abc import ABC, abstractmethod
from eo4eu_base_utils.result import Result


class Source(ABC):
    """A generic class which represents any data source
    It gets a list of arguments, which is meant to represent
    nested keys, and returns a ``eo4eu_base_utils.result.Result``
    (refer to eo4eu_base_utils documentation for more details)
    """

    @abstractmethod
    def get(self, args: list) -> Result:
        """Get the data specified by the `args` path/nested keys

        :param args: The path/nested keys to source data from
        :type args: List
        :rtype: eo4eu_base_utils.result.Result
        """
        return Result.err("")


class Filler(ABC):
    """A generic class meant to contain logic for getting
    data out of sources. They may, for example, manipulate
    given data in some way, or provide a default if a failure
    happened
    """

    @abstractmethod
    def fill(self, source: Source, val: Result) -> Result:
        """Given a source and a previous value, produce a new value.

        :param source: The source of the data
        :type source: Source
        :param val: A result coming from previous fillers
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        return None

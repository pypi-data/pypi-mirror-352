import logging
from pathlib import Path
from eo4eu_base_utils import if_none
from eo4eu_base_utils.unify import overlay
from eo4eu_base_utils.typing import Callable, Any, List, Dict, Iterator

from .model import Action, Data
from ..settings import Settings
from ..metainfo import DSMetainfo


class NoOp(Action):
    """Action that does nothing

    :param args: Ignored
    :param kwargs: Ignored
    """

    def __init__(self, *args, **kwargs):
        pass

    def act(self, input: Data) -> Data:
        """Does nothing, returning the Data object unchanged

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        return input


class Apply(Action):
    """Action wrapping a function that transforms Data objects
    to other Data objects

    :param func: A function which transforms entire Data objects (NOT single elements!)
    :type func: Callable[[Data],Data]
    :param kwargs: Passed to the function
    :type kwargs: Dict[str,Any]
    """

    def __init__(self, func: Callable[[Data],Data], **kwargs):
        self._func = func
        self._kwargs = kwargs

    def act(self, input: Data) -> Data:
        """Calls the function on the input

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        return self._func(input, **self._kwargs)


class Map(Action):
    """An action wrapping a function that transforms individual
    data points. Each data point may be transformed to one or 
    more data points of the same or a different type

    :param map_func: A function which transforms individual data points
    :type map_func: Callable[[Any],Any]
    :param iter_func: An optional function which iterates over Data objects (default: :obj:`eo4eu_data_utils.stream.Data.passed`)
    :type iter_func: Callable[[Data],Iterator[Any]]|None
    :param append_func: An optional function which appends the data to the result's .passed list. By default, this is list.append, but it might be changed to list.extend if the function returns multiple results (prime example of this is unpacking archives, an operation which generates several files for each archive)
    :type append_func: Callable[[List[Any],Any],None]|None
    :param pre_callback: Optional function to call before the map function is called. It takes as arguments the entire input Data object, the list of successful map results so far, the list of failed map results so far, and the current item to be mapped. By default, it does nothing.
    :type pre_callback: Callable[[Data,List[Any],List[Any],Any],None]|None
    :param post_callback: Optional function to call after the map function is called. It takes as arguments the entire input Data object, the list of successful map results so far, the list of failed map results so far, and the item that was just mapped. By default, it does nothing.
    :type post_callback: Callable[[Data,List[Any],List[Any],Any],None]|None
    :param err_callback: Optional function to call whenever `pre_callback`, `map_func` or `append_func` raises an exception. By default, it is what is returned by :func:`eo4eu_data_utils.settings.Settings.make_default_err_callback`, using the name passed in the `name` parameter.
    :type err_callback: Callback[[Any,Exception],Any]|None
    :param post_err_callback: Optional function to call whenever `post_callback` raises an exception. By default, it logs the error as a warning using the :obj:`eo4eu_data_utils.settings.Settings.LOGGER` logger.
    :type post_err_callback: Callback[[Any,Exception],Any]|None
    :param name: Optional name for the operation (default: "map")
    :type name: str
    :param kwargs: Keyword arguments passed to `map_func` every time it's called
    :type kwargs: Dict[str,Any]
    """

    def __init__(
        self,
        map_func: Callable[[Any],Any],
        iter_func: Callable[[Data],Iterator[Any]]|None = None,
        append_func: Callable[[List[Any],Any],None]|None = None,
        pre_callback: Callable[[Data,List[Any],List[Any],Any],None]|None = None,
        post_callback: Callable[[Data,List[Any],List[Any],Any],None]|None = None,
        err_callback: Callable[[Any,Exception],Any]|None = None,
        post_err_callback: Callable[[Any,Exception],Any]|None = None,
        name: str = "map",
        **kwargs
    ):
        self._map_func = map_func
        self._iter_func = if_none(iter_func, lambda data: data.passed)
        self._append_func = if_none(append_func, lambda ls, item: ls.append(item))
        self._pre_callback = if_none(pre_callback, lambda input, passed, failed, item: None)
        self._post_callback = if_none(post_callback, lambda input, passed, failed, item: None)
        self._err_callback = if_none(
            err_callback,
            Settings.make_default_err_callback(name)
        )
        self._post_err_callback = if_none(
            post_err_callback,
            lambda item, e: Settings.LOGGER.warning(f"Post map callback failed: {e}")
        )
        self._kwargs = kwargs

    def act(self, input: Data) -> Data:
        """Transform each relevant (relevant here defined by the object's `iter_func`)
        element in the input using `map_func`. If the
        function raises an exception, the element is placed in the output's
        failed list. The Data object's metainfo is not changed

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        passed, failed = [], []
        for item in self._iter_func(input):
            try:
                self._pre_callback(input, passed, failed, item)
                result = self._map_func(item, **self._kwargs)
                self._append_func(passed, result)
            except Exception as e:
                self._err_callback(item, e)
                failed.append(item)

            try:
                self._post_callback(input, passed, failed, item)
            except Exception as e:
                self._post_err_callback(item, e)

        return input.but(passed = passed, failed = failed)


# This is a Callable[[Any],List[Any]]
class TransferMap:
    """This is NOT an :class:`eo4eu_data_utils.stream.Action`, but
    rather a ``Callable[[Any],Any]``! It is meant to be a general
    template for file transfer operations, whether those are
    uploads, downloads, moves, archive unpacks, etc...

    :param dst_func: A function which takes some source path and creates a destination path. For example, it may be one which takes filepaths and returns other filepaths with the same name but in a different, predefined directory. Technically, "paths" here don't have to be instances of :class:`pathlib.Path` or :class:`eo4eu_data_utils.stream.PathSpec`, but if they are to be used with instances of :class:`eo4eu_data_utils.stream.Downloader` or :class:`eo4eu_data_utils.stream.Uploader`, they should be instances of :class:`eo4eu_data_utils.stream.PathSpec`.
    :type dst_func: Callable[[Any],Any]
    :param transfer_func: A function which transfers an object to wherever `dst_func` points to, and returns the final path
    :type transfer_func: Callable[[Any,Any],Any]
    :param logger: A standard Python logger (default: :obj:`eo4eu_data_utils.settings.Settings.LOGGER`)
    :type logger: logging.Logger|None
    :param name: The name of the operation to be used in logs (default: "Transferring")
    :type name: str
    :param kwargs: Keyword arguments passed to each call of transfer_func
    :type kwargs: Dict[str,Any]
    """

    def __init__(
        self,
        dst_func: Callable[[Any],Any],
        transfer_func: Callable[[Any,Any],Any],
        logger: logging.Logger|None = None,
        name: str = "Transferring",
        **kwargs
    ):
        self._dst_func = dst_func
        self._transfer_func = transfer_func
        self._logger = if_none(logger, Settings.LOGGER)
        self._name = name
        self._spaces = " " * (len(self._name) - 3)
        self._kwargs = kwargs

    def __call__(self, src: Any) -> Any:
        self._logger.info(f"{self._name} {src}")
        dst = self._dst_func(src)
        result = self._transfer_func(src, dst, **self._kwargs)

        prefix = f"{self._spaces} to "
        if isinstance(result, list):
            head, tail = result[0], result[1:]
            self._logger.info(f"{prefix}{head}")
            for item in tail:
                self._logger.info(f"{self._spaces}    {item}")
        else:
            self._logger.info(f"{prefix}{result}")

        return result


# This is a Callable[[Any],List[Any]]
class FilterMap:
    """This is NOT an :class:`eo4eu_data_utils.stream.Action`, but
    rather a ``Callable[[Any],Any]``! It is meant to be a general
    template for filter operations, meaning ones which exclude
    objects based on some predicate

    :param predicate: A function which checks if an object should be kept or not
    :type predicate: Callable[[Any],bool]
    """
    def __init__(self, predicate: Callable[[Any],bool]):
        self._predicate = predicate

    def __call__(self, src: Any) -> List[Any]:
        if self._predicate(src):
            return src
        else:
            name = "[unknown]"
            try:
                name = self._predicate.__name__
            except Exception:
                pass
            raise ValueError(
                f"Item \"{src}\" failed to satisfy filter \"{name}\""
            )


class Overlay(Action):
    """An action for transforming the metadata dictionary of Data objects

    :param args: Ignored
    :param kwargs: The dictionary to overlay with the one of the Data object
    :type kwargs: Dict[str,Any]
    """

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs

    def act(self, input: Data) -> Data:
        """Use :func:`eo4eu_base_utils.unify.overlay` to combine this
        action's keyword args with the Data object's metadata dictionary

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        return input.but(kwargs = overlay(input.kwargs, self._kwargs))


class Source(Action):
    """An action for adding new data points to the Data object

    :param source: A function that takes no params and returns a filled Data object
    :type source: Callable[[],Data]
    :param err_callback: An optional function to be called when `source` raises an error
    :type err_callback: Callable[[Any,Exception],Any]|None
    """

    def __init__(
        self,
        source: Callable[[],Data],
        err_callback: Callable[[Any,Exception],Any]|None = None,
        **kwargs
    ):
        self._source = source
        self._err_callback = if_none(
            err_callback,
            Settings.make_default_err_callback("source")
        )

    def act(self, input: Data) -> Data:
        """Take the result of `source` and :func:`eo4eu_data_utils.stream.Data.merge`
        it with the input Data object

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        result = Data.empty()
        try:
            result = self._source()
        except Exception as e:
            self._err_callback(self._source.__name__, e)

        return input.merge(result)


class Switch(Action):
    """An action that implements control flow using pairs of
    predicates and other actions.

    :param cases: A list of pairs of predicates and actions. If an element of the incoming Data object matches the predicate, it will be added to a new Data object that is then passed to the appropriate action. Warning: An object may match at most one predicate! It will only be added to the first action whose predicate is matched
    :type cases: List[tuple[Callable[[Any],bool], Action]]
    :param iter_func: An optional function which iterates over Data objects (default: :obj:`eo4eu_data_utils.stream.Data.passed`)
    :type iter_func: Callable[[Data],Iterator[Any]]|None
    :param err_callback: An optional function to be called when an error is raised
    :type err_callback: Callable[[Any,Exception],Any]|None
    :param default: Akin to the default case on a switch. If an item doesn't match any of the cases, it will go through this action. If this argument is None, the items which match no cases will be discarded (they won't be added to the result's failed list)
    :type default: Action|None
    """

    def __init__(
        self,
        cases: List[tuple[Callable[[Any],bool],Action]],
        iter_func: Callable[[Data],Iterator[Any]]|None = None,
        err_callback: Callable[[Any, Exception],Any]|None = None,
        default: Action|None = None,
        **kwargs
    ):
        self._cases = cases.copy()
        if default is not None:
            self._cases.append((lambda item: True, default))

        self._iter_func = if_none(iter_func, lambda data: data.passed)
        self._err_callback = if_none(
            err_callback,
            Settings.make_default_err_callback("switch")
        )

    def act(self, input: Data) -> Data:
        """Split the input Data object into N Data objects, where N
        is this action's number of cases. The way this happens is written
        in the `cases` parameter description. Each Data object is passed through
        the appropriate function, and subsequently merged using
        :class:`eo4eu_data_utils.stream.Data.merge`. The input's metadata are
        passed as-is into each of the N Data objects

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        groups = [[] for _ in self._cases]
        for item in self._iter_func(input):
            try:
                for idx, (predicate, _) in enumerate(self._cases):
                    if predicate(item):
                        groups[idx].append(item)
                        break
            except Exception as e:
                self._err_callback(item, e)
                failed.append(item)

        result = Data.empty()
        for (_, action), data in zip(self._cases, groups):
            try:
                result = result.merge(action.act(Data(
                    passed = data,
                    failed = [],
                    kwargs = input.kwargs
                )))
            except Exception as e:
                self._err_callback(data, e)

        return result


class Report(Action):
    """Action that calls some function with side-effects whenever
    a condition is met. The output is not changed

    :param trigger_func: A predicate that is called on the input object and returns a boolean. If True, `report_func` is called (default: ``lambda data: True``)
    :type trigger_func: Callable[[Data],bool]|None
    :param report_func: A function that is called on the input Data object if `trigger_func` returns True on it (default: logs the data object under "eo4eu.data" with level logging.INFO)
    :type report_func: Callable[[Data],None]|None
    :param kwargs: Ignored
    """

    def __init__(
        self,
        trigger_func: Callable[[Data],bool]|None = None,
        report_func: Callable[[Data],None]|None = None,
        **kwargs
    ):
        self._trigger_func = if_none(trigger_func, lambda data: True)
        self._report_func = if_none(report_func, lambda data: Settings.LOGGER.info(data))

    def act(self, input: Data) -> Data:
        """Call `report_func` if `trigger_func` is True, leaving the Data object
        unchanged

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        try:
            if self._trigger_func(input):
                self._report_func(input)
        except Exception as e:
            Settings.LOGGER.warning(f"Failed to report: {e}")

        return input


class Rename(Action):
    """Action that ONLY works with Data objects that contain
    :class:`eo4eu_data_utils.stream.PathSpec` items. It needs a method
    by which to shorten the PathSpec's paths, subsequently using the
    shortened paths as names to the PathSpecs.

    :param method: A function which takes a list of :class:`pathlib.Path` s and returns another one. It is meant to shorten them in order to have more convenient names, but in principle it may do anything
    :type method: Callable[[List[Path]],List[Path]]
    :param err_callback: An optional function to be called when an error is raised
    :type err_callback: Callable[[Any,Exception],Any]|None
    :param kwargs: The keyword arguments that will be passed to `method`
    :type kwargs: Dict[str,Any]
    """

    def __init__(
        self,
        method: Callable[[List[Path]],List[Path]],
        err_callback: Callable[[Any,Exception],Any]|None = None,
        **kwargs
    ):
        self._method = method
        self._err_callback = if_none(
            err_callback,
            Settings.make_default_err_callback("rename")
        )
        self._kwargs = kwargs

    def act(self, input: Data) -> Data:
        """Runs the `method` function on a list made up of the path fields of
        each PathSpec in the input. If the resulting list has a different length
        to the incoming one, the input is returned unchanged. If it has the same
        length, the resulting paths are placed in the name field of the PathSpecs.
        It is assumed that `method` returns paths in the same order they were given

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        try:
            old_names = [
                pathspec.name for pathspec in input.passed
            ]
            new_names = self._method(old_names, **self._kwargs)
            if len(new_names) != len(old_names):
                raise ValueError(
                    f"Method \"{self._method.__name__}\" returned {len(new_names)} paths, "
                    f"expected {len(old_names)}"
                )

            return input.but(passed = [
                (item.but(name = name) if name is not None else item)
                for item, name in zip(input.passed, new_names)
            ])
        except Exception as e:
            self._err_callback(input, e)

        return input


class FillMetainfo(Action):
    """Action that tries to fill metainfo field of 
    :class:`eo4eu_data_utils.stream.PathSpec` objects, though
    it is flexible enough to handle any object that has a method
    that gets some :class:`pathlib.Path` representing its path,
    one which returns some :class:`pathlib.Path` representing its name
    and one that sets some metainfo dictionary.

    :param metainfo: The metainfo of the dataset
    :type metainfo: DSMetainfo
    :param distance: A function which determines how \"compatible\" a product ID is with a path. It returns a number; the larger it is, the further away the two IDs are. If it is negative, they are considered \"infinitely\" far away. For example, a distance function may return 0 if the ID equals the path name and -1 if it does not
    :type distance: Callable[[str,Path],float]
    :param method: A function which takes a distance matrix and returns a vector of matched indices. On the X axis, the matrix has the input paths. On the Y axis, it has the product IDs from the metainfo. X and Y values are matched based, in some way, on how large the distances between them are.
    :type method: Callable[[List[List[float]]],List[int]]
    :type default: A function which returns the default metainfo for a given path, in case the method was unable to match it to any product found in the dataset's metainfo. By default, it simply returns ``{product_id: name}``
    :type default: Callable[[Any],Dict]
    :param product_id: The metainfo key (or getter) which corresponds to the ID of each product (default: "id")
    :type product_id: Callable[[Dict],str]|str
    :param path_getter: A function which gets the path of the incoming object. By default, it tries getting the ``.path`` attribute
    :type path_getter: Callable[[Any],Path]|None
    :param name_getter: A function which gets the name of the incoming object. By default, it tries getting the ``.name`` attribute
    :type name_getter: Callable[[Any],name]|None
    :param meta_setter: A function which returns the incoming object with the desired metainfo set to it. By default, it tries setting the ``.meta["meta"]`` attribute/key
    :type meta_setter: Callable[[Any,Dict],Any]|None
    :param err_callback: An optional function to be called when an error is raised
    :type err_callback: Callable[[Any,Exception],Any]|None
    :param kwargs: Ignored
    """

    def __init__(
        self,
        metainfo: DSMetainfo,
        distance: Callable[[str,Path],float],
        method: Callable[[List[List[float]]],List[int]],
        default: Callable[[Any],Dict]|None = None,
        product_id: Callable[[Dict],str]|str = "id",
        path_getter: Callable[[Any],Path]|None = None,
        name_getter: Callable[[Any],Path]|None = None,
        meta_setter: Callable[[Any,Dict],Any]|None = None,
        err_callback: Callable[[Any,Exception],Any]|None = None,
        **kwargs
    ):
        if isinstance(product_id, str):
            self._product_id_str = product_id
            self._product_id = lambda product: product[product_id]
        else:
            self._product_id_str = "id"
            self._product_id = product_id

        self._metainfo = metainfo
        self._distance = distance
        self._method = method
        self._path_getter = if_none(path_getter, lambda pathspec: pathspec.path)
        self._name_getter = if_none(name_getter, lambda pathspec: pathspec.name)
        self._meta_setter = if_none(meta_setter, lambda pathspec, meta: pathspec.but(
            meta = overlay(pathspec.meta, {"meta": meta})
        ))
        self._default = if_none(default, lambda item: {self._product_id_str: str(self._name_getter(item))})
        self._err_callback = if_none(
            err_callback,
            Settings.make_default_err_callback("fill metainfo for")
        )

    def _default_result(self, input: Data) -> Data:
        return input.but(passed = [
            self._meta_setter(item, self._default(item))
            for item in input
        ])

    def act(self, input: Data) -> Data:
        """Try and fill the metainfo of the (passed) items in the input Data
        object. It first calculates the distance matrix by using the `distance`
        function on all combinations of input paths and product IDs in the
        metainfo. It then passes that matrix to the `method` function to get
        matches. If matched, the input item gets that particular metainfo.
        Otherwise, the `default` method is used on the item to fill its metainfo.
        If something blows up in the process, all items are given the default
        metainfo. If that blows up as well, the input is returned as-is

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        try:
            if len(self._metainfo.products) <= 0:
                raise ValueError(f"Given metainfo has no products")

            distance_matrix = [
                [
                    self._distance(self._product_id(product), self._path_getter(item))
                    for product in self._metainfo.products
                ]
                for item in input
            ]
            matches = self._method(distance_matrix)
            if len(matches) != input.len():
                raise ValueError(
                    f"Method \"{self._method.__name__}\" returned {len(matches)} matches, "
                    f"expected {input.len()}"
                )

            result = []
            for item, match_idx in zip(input, matches):
                meta = None
                if match_idx < 0:
                    meta = self._default(item)
                else:
                    try:
                        meta = self._metainfo.products[match_idx]
                    except Exception as e:
                        self._err_callback(item, e)
                        meta = self._default(item)

                result.append(self._meta_setter(item, meta))

            return input.but(passed = result)
        except Exception as e:
            self._err_callback(self._metainfo.name(), e)

        try:
            return self._default_result(input)
        except Exception as e:
            self._err_callback(self._metainfo.name(), e)
            return input

import logging
import functools
import mimetypes
from pathlib import Path
from eo4eu_base_utils import if_none
from eo4eu_base_utils.unify import overlay
from eo4eu_base_utils.typing import Any, List, Self, Callable

from .actions import (
    NoOp,
    Apply,
    Map,
    TransferMap,
    FilterMap,
    Source,
    Switch,
    Report,
    Rename,
    FillMetainfo,
)
from .drivers import LocalDriver
from .model import Data, Action, PathSpec, Downloader, Uploader, Lister
from ..helpers.unpack import unsafe_unpack
from ..metainfo import DSMetainfo
from ..settings import Settings


class Stream(Action):
    """A wrapper class around all the default actions. It represents
    a sequence of actions to be executed one after the other, i.e.
    a data processing pipeline. It is
    generally expected that the user will use this class instead
    of instantiating :class:`eo4eu_data_utils.stream.Action` objects
    directly, potentially defining their own Action objects. This
    constructor will typically be called without arguments.

    :param actions: The pipeline of actions to be called
    :type actions: List[Action]|None
    :param recovery_method: A function that gets called if one of the actions in the pipeline raises an exception. Actions are not supposed to do this, but this is a guard against developer error. Basically, if an action blows up, `recovery_method` is called on its input instead, and the output is then sent to the next action. Can also be a string referring to one of the default recovery methods, found in :obj:`eo4eu_data_utils.settings.Settings.RECOVERY_METHODS` (default: "soft_fail")
    :type recovery_method: Callable[[Data,Exception],Data]|str
    :param recovery_callback: A function to be called before `recovery_method` is called, for the purpose of logging the failure. By default, it uses :func:`eo4eu_data_utils.settings.Settings.make_default_err_callback`
    :type recovery_callback: Callable[[str,Exception],None]|None
    :param kwargs: A set of keyword arguments to be substituted in action constructors
    :type kwargs: Dict[str,Any]
    """

    def __init__(
        self,
        actions: List[Action]|None = None,
        recovery_method: Callable[[Data,Exception],Data]|str = "soft_fail",
        recovery_callback: Callable[[str,Exception],None]|None = None,
        **kwargs
    ):
        recovery_callback = if_none(
            recovery_callback,
            Settings.make_default_err_callback("execute")
        )
        if isinstance(recovery_method, str):
            recovery_method = Settings.RECOVERY_METHODS.get(recovery_method)

        self._actions = if_none(actions, [])
        self._recovery_method = recovery_method
        self._recovery_callback = recovery_callback
        self._kwargs = kwargs

    def act(self, input: Data) -> Data:
        """Run the action pipeline on some input Data object

        :param input: The input data
        :type input: Data
        :rtype: Data
        """
        result = input
        for action in self._actions:
            try:
                result = action.act(result)
            except Exception as e:
                self._recovery_callback(action.__class__.__name__, e)
                result = self._recovery_method(result, e)

        return result

    def exec(self) -> Data:
        """Call :func:`eo4eu_data_utils.stream.Stream.act` with an
        empty Data object, as returned by :func:`eo4eu_data_utils.stream.Data.empty`

        :rtype: Data
        """
        return self.act(Data.empty())

    def then(self, action: Action) -> Self:
        """Add an action to the end of the pipeline

        :param action: Any class conforming to the Action interface
        :type action: Action
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        self._actions.append(action)
        return self

    def then_init(self, action_constructor: Callable[[Any],Any], *args, **kwargs):
        """Construct an action and add it to the end of the pipeline.
        This method will add the keys in the `kwargs` field of the Stream to the
        constructor, unless the keys already exist in the call
        of this function

        :param action_constructor: A function which take some positional and keyword arguments and returns an action
        :type action_constructor: Callable[[Any],Any]
        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then(action_constructor(
            *args, **(self._kwargs | kwargs)
        ))

    def then_if(self, if_true: bool, action: Action) -> Self:
        """Add an action to the end of the pipeline, only if the
        `if_true` parameter is True. Otherwise, do nothing

        :param if_true: Whether or not to add the action
        :type if_true: bool
        :param action: Any class conforming to the Action interface
        :type action: Action
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        if if_true:
            return self.then(action)
        return self

    def apply(self, *args, **kwargs) -> Self:
        """Add an :class:`eo4eu_data_utils.stream.actions.Apply` action
        to the end of the pipeline

        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(Apply, *args, **kwargs)

    def map(self, *args, **kwargs) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Map` action
        to the end of the pipeline

        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(Map, *args, **kwargs)

    def source(self, *args, **kwargs) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Source` action
        to the end of the pipeline

        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(Source, *args, **kwargs)

    def ls(
        self,
        lister: Lister|None = None,
        src: Path|str|None = None,
        **kwargs
    ) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Source` action
        to the end of the pipeline. This source is instantiated by using a
        :class:`eo4eu_data_utils.stream.Lister`. Basically, the source calls
        the lister on the `src` parameter and returns a list of pathspecs to
        be added to the data.

        :param lister: A lister to be used for listing PathSpecs. If this field is a string or a :class:`pathlib.Path`, it will be assumed that it refers to the `src` parameter and the default lister (:class:`eo4eu_data_utils.stream.LocalDriver`) is used
        :type lister: Lister
        :param src: The source directory to list
        :type src: Path|str|None
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        if (isinstance(lister, str) or isinstance(lister, Path)) and src is None:
            src = Path(lister)
            lister = None

        lister = if_none(lister, LocalDriver())
        src = Path(if_none(src, ""))
        return self.then_init(
            Source,
            source = lambda: Data(passed = lister.ls(src), failed = [], kwargs = {}),
            **kwargs
        )

    def raw(self, items: List[Any], **kwargs) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Source` action
        to the end of the pipeline, which simply creates a Data object
        with the provided list of items in the ``passed`` field

        :param items: A list of items
        :type items: List[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(
            Source,
            source = lambda: Data(passed = items, failed = [], kwargs = {}),
            **kwargs
        )

    def transfer(
        self,
        dst_func: Callable[[PathSpec],PathSpec],
        transfer_func: Callable[[PathSpec,PathSpec],List[PathSpec]],
        logger: logging.Logger|None = None,
        transferring: str = "Transferring",
        transfer: str = "transfer",
        **kwargs
    ) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Map` action
        to the end of the pipeline, in particular one which wraps a
        :class:`eo4eu_data_utils.stream.actions.TransferMap` callable.
        This function is the basis for download, upload and unpack functions
        and should probably not be used directly. The resulting action only
        works on Data objects with items of type :class:`eo4eu_data_utils.stream.PathSpec`

        :param dst_func: A function which looks at a PathSpec and decides what PathSpec it should become. For example, it may want to change its parent directory or its extension
        :type dst_func: Callable[[PathSpec],PathSpec]
        :param transfer_func: A function which \"moves\" the PathSpec from where it is to where `dst_func` tells it to. \"Moves\" here may refer to filesystem moves, downloads, uploads, unpacks, etc...
        :type transfer_func: Callable[[PathSpec,PathSpec],PathSpec|List[PathSpec]]
        :param logger: Optional logger for printing messages (default: :class:`eo4eu_data_utils.settings.Settings.LOGGER`)
        :param transferring: The verb to use when logging the actions taken (default: "Transferring")
        :type transferring: str
        :param transfer: The verb to use when logging errors (default: "transfer", as in "Failed to transfer")
        :type transfer: str
        :type logger: logging.Logger|None
        :param kwargs: The keyword arguments to be passed into the Map constructor.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        logger = if_none(logger, Settings.LOGGER)

        return self.map(**({
            "map_func": TransferMap(
                dst_func = dst_func,
                transfer_func = transfer_func,
                logger = logger,
                name = transferring
            ),
            "err_callback": lambda item, e: logger.warning(f"Failed to {transfer} {item}: {e}"),
        } | kwargs))

    def download(self, downloader: Downloader, dst: Path|str|None = None, **kwargs) -> Self:
        """Uses :func:`eo4eu_data_utils.stream.Stream.transfer` to execute a download
        using the provided downloader

        :param downloader: The downloader to use
        :type downloader: Downloader
        :param dst: The destination directory to place the files into (default: current directory)
        :type dst: Path|str|None
        :param kwargs: Additional keyword arguments to be passed into the Stream.transfer call.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        dst = if_none(dst, Path.cwd())

        return self.transfer(**({
            "dst_func":      _get_default_dst_func(dst),
            "transfer_func": functools.partial(_download_func, downloader = downloader),
            "transferring":  "Downloading",
            "transfer":      "download",
        } | kwargs))

    def upload(self, uploader: Uploader, dst: Path|str|None = None, **kwargs) -> Self:
        """Uses :func:`eo4eu_data_utils.stream.Stream.transfer` to execute a upload
        using the provided uploader

        :param uploader: The uploader to use
        :type uploader: Uploader
        :param dst: The destination directory to place the files into (default: current directory)
        :type dst: Path|str|None
        :param kwargs: Additional keyword arguments to be passed into the Stream.transfer call.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        dst = if_none(dst, Path.cwd())

        return self.transfer(**({
            "dst_func":      _get_default_dst_func(dst),
            "transfer_func": functools.partial(_upload_func, uploader = uploader),
            "transferring":  "Uploading",
            "transfer":      "upload",
        } | kwargs))

    def move(self, dst: Path|str|None = None, **kwargs) -> Self:
        """Uses :func:`eo4eu_data_utils.stream.Stream.transfer` to execute a
        filesystem move to the `dst` directory

        :param dst: The destination directory to move the files into (default: current directory)
        :type dst: Path|str|None
        :param kwargs: Additional keyword arguments to be passed into the Stream.transfer call.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        dst = if_none(dst, Path.cwd())

        return self.transfer(**({
            "dst_func":      _get_default_dst_func(dst),
            "transfer_func": _move_func,
            "transferring":  "Moving",
            "transfer":      "move",
        } | kwargs))

    def unpack(self, dst: Path, **kwargs) -> Self:
        """Uses :func:`eo4eu_data_utils.stream.Stream.transfer` to unpack
        all archives to the `dst` directory. If a file in the input is not
        an archive, it is left as-is

        :param dst: The destination directory to unpack the files into (default: current directory)
        :type dst: Path|str|None
        :param kwargs: Additional keyword arguments to be passed into the Stream.transfer call.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.transfer(**({
            "dst_func":      _get_default_dst_func(dst),
            "transfer_func": _unpack_func,
            "append_func":   lambda ls, items: ls.extend(items),
            "transferring":  "Unpacking",
            "transfer":      "unpack",
        } | kwargs))

    def filter(
        self,
        predicate: Callable[[Any],bool],
        drop_failed: bool = True,
        **kwargs
    ) -> Self:
        """Use a predicate to decide whether or not to keep
        items in the Data object

        :param predicate: A function that returns True if the object is valid and False if it is not
        :type predicate: Callable[[Any],bool]
        :param drop_failed: If True, the files rejected by the predicate are removed from the Data object. If False, they are simply moved to the Data object's ``failed`` list. (default: True)
        :param kwargs: The keyword arguments to be passed into the Map constructor.
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        result = self.map(**({
            "map_func":     FilterMap(predicate),
            "err_callback": lambda item, e: None,
        } | kwargs))
        if drop_failed:
            return result.drop_failed()
        else:
            return result

    def switch(self, *args, **kwargs) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Switch` action
        to the end of the pipeline

        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(Switch, *args, **kwargs)

    def ifelse(
        self,
        predicate: Callable[[Any],bool],
        if_action: Action,
        else_action: Action,
        **kwargs
    ) -> Self:
        """Implements basic control flow using a predicate. Each item in the
        Data object is passed through the predicate. If it returns True, it is
        passed to the `if_action`. If it is False, it is passed to the `else_action`.
        The results of both actions are merged and returned.

        :param predicate: A function which takes an item and returns a bool
        :type predicate: Callable[[Any],bool]
        :param if_action: Takes a Data object containing all items on which predicate returns True
        :type if_action: Action
        :param else_action: Takes a Data object containing all items on which predicate returns False
        :type else_action: Action
        :param kwargs: Extra keyword arguments to be passed into Stream.switch
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.switch(**({
            "cases": [
                (predicate, if_action),
                (lambda item: True, else_action),
            ],
        } | kwargs))

    def branch(
        self,
        predicate: Callable[[Any],bool],
        action: Action,
        **kwargs
    ) -> Self:
        """Implements basic control flow using a predicate. Each item in the
        Data object is passed through the predicate. If it returns True, it is
        passed to the action. If it is False, it is not changed at all. In the
        end, all items are merged into the output Data object

        :param predicate: A function which takes an item and returns a bool
        :type predicate: Callable[[Any],bool]
        :param action: Takes a Data object containing all items on which predicate returns True
        :type action: Action
        :param kwargs: Extra keyword arguments to be passed into Stream.switch
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.ifelse(predicate, action, NoOp(), **kwargs)

    def report(self, *args, **kwargs) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Report` action
        to the end of the pipeline

        :param args: The positional arguments to be passed into the constructor
        :type args: tuple[Any]
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.then_init(Report, *args, **kwargs)

    def warn(
        self,
        func: Callable[[tuple[int,int]],None]|str = "Failed: {}/{} items",
        **kwargs
    ) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Report` action
        to the end of the pipeline. By default, `func` is only called when
        there is one or more item in the ``.failed`` field of the Data
        object. Instead of a function, you may pass a format string which
        takes two arguments, the number of failed items and the total number
        of items. An example of a format string would be \"Failed to download {}/{} files\"

        :param func: A function which takes in two integers: the number of failed items and the total number of items in the Data object. It may be a format string that does the same, instead (default: \"Failed: {}/{} items\")
        :type func: Callable[[tuple[int,int]],None]|str
        :param kwargs: Extra keyword arguments to be passed into Stream.report
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        report_func = func
        if isinstance(func, str):
            report_func = lambda failed, total: Settings.LOGGER.warning(
                func.format(failed, total)
            )

        return self.report(**({
            "trigger_func": lambda data: data.any_failed(),
            "report_func":  lambda data: report_func(*data.warn_stats())
        } | kwargs))

    def drop_failed(self) -> Self:
        """Add an action to the end of the pipeline which does nothing
        except remove all items from the ``.failed`` field in the Data
        object

        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.apply(lambda data: data.but(failed = []))

    def drop(self) -> Self:
        """Add an action to the end of the pipeline which removes
        all items from both the ``.passed`` and ``.failed``
        fields in the Data object

        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        return self.apply(lambda data: data.but(passed = [], failed = []))

    def rename(
        self,
        method: Callable[[List[Path]],List[Path]]|str = "trim_root",
        **kwargs
    ) -> Self:
        """Add a :class:`eo4eu_data_utils.stream.actions.Rename` action
        to the end of the pipeline. The method may be a string

        :param method: A rename method, as described in :class:`eo4eu_data_utils.stream.actions.Rename`. If a string is passed, it will be used as the key to :obj:`eo4eu_data_utils.settings.Settings.RENAME_METHODS` (default: \"shortest_unique\")
        :type method: Callable[[List[Path]],List[Path]]|str
        :param kwargs: The keyword arguments to be passed into the constructor. Fields from the `kwargs` field of the stream will be added to it, if they don't already exist
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        if isinstance(method, str):
            method = Settings.RENAME_METHODS.get(method)

        return self.then_init(
            Rename,
            **({"method": method} | kwargs)
        )

    def do(
        self,
        func: Callable[[Any],None],
        *args,
        **kwargs
    ):
        """Add an action to the end of the pipeline which calls
        a function with the given `args` and `kwargs` and returns
        the input Data object

        :param func: A function which has nothing to do with Data objects
        :type func: Callable[[Any],None]
        :param args: The positional arguments which will be passed to the function
        :type args: tuple[Any]
        :param kwargs: The keyword arguments which will be passed to the function
        :type kwargs: Dict[str,Any]
        """
        def _sub_func(input, *args, **kwargs):
            func(*args, **kwargs)
            return input

        return self.apply(
            func = functools.partial(_sub_func, *args, **kwargs)
        )

    def fill_metainfo(
        self,
        metainfo: DSMetainfo,
        distance: Callable[[str,Path],float]|str = "group_distance",
        method: Callable[[List[List[float]]],List[int]]|str = "unique_sort_match",
        **kwargs
    ):
        """Add a :class:`eo4eu_data_utils.stream.actions.FillMetainfo` action
        to the end of the pipeline

        :param metainfo: The dataset's metainfo
        :type metainfo: DSMetainfo
        :param distance: The distance function to use. Can be a string which refers to one of the builtin distance functions, found in :obj:`eo4eu_data_utils.settings.Settings.STRING_DISTANCE_METHODS` (default: \"group_distance\")
        :type distance: Callable[[str,Path],float]|str
        :param method: The distance function to use. Can be string which refers to one of the builtin fill metainfo functions, found in :obj:`eo4eu_data_utils.settings.Settings.FILL_META_METHODS` (default: \"unique_sort_match\")
        :type method: Callable[[List[List[float]]],List[int]]|str
        :param kwargs: The keyword arguments to be passed into the constructor
        :type kwargs: Dict[str,Any]
        :returns: Itself (the Stream object is modified inplace!)
        :rtype: Stream
        """
        if isinstance(distance, str):
            distance = Settings.STRING_DISTANCE_METHODS.get(distance)
        if isinstance(method, str):
            method = Settings.FILL_META_METHODS.get(method)

        return self.then_init(
            FillMetainfo,
            **({
                "metainfo": metainfo,
                "distance": distance,
                "method":   method,
            } | kwargs)
        )


def _base_default_dst_func(src: PathSpec, dst: Path) -> PathSpec:
    return src.but(
        name = src.name,
        path = dst.joinpath(src.name)
    )


def _get_default_dst_func(dst: Path|str) -> Callable[[PathSpec],PathSpec]:
    return functools.partial(_base_default_dst_func, dst = Path(dst))


def _move_func(src: PathSpec, dst: PathSpec) -> PathSpec:
    dst.path.parent.mkdir(parents = True, exist_ok = True)
    src.path.rename(dst.path)
    return dst


def _download_func(src: PathSpec, dst: PathSpec, downloader: Downloader) -> PathSpec:
    return downloader.download(src, dst)


def _upload_func(src: PathSpec, dst: PathSpec, uploader: Uploader) -> PathSpec:
    return uploader.upload(src, dst)


def _unpack_func(src: PathSpec, dst: PathSpec) -> List[PathSpec]:
    if mimetypes.guess_type(src.path)[0] in [
        "application/x-tar",
        "application/zip",
    ]:
        return [
            src.but(
                name = out_path.relative_to(dst.path.parent),
                path = out_path
            )
            for out_path in unsafe_unpack(src.path, dst.path)
        ]
    else:
        return [src]

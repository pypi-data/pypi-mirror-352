import logging
from pathlib import Path
from eo4eu_base_utils.typing import Any, Callable, Self, Iterator
from eo4eu_base_utils.result import Result
from eo4eu_base_utils import if_none

from .model import Filler, Source
from .utils import _to_bool, _to_list

from ..settings import Settings

logger = logging.getLogger("eo4eu.data")


class DependencyFiller(Filler):
    """This filler tries to use a different filler, if available.
    This is for use in fillers which need to call other
    fillers recursively.

    :param value: Either a filler, in which case it will be used, or something else, in which case it will always return this value
    :type value: Filler|Any
    """

    def __init__(self, value: Filler|Any):
        self._value = value

    def fill(self, source: Source, val: Result) -> Result:
        """If self.value is a filler, try and use it to fill the result.
        Otherwise, return Result.ok(self.value).

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if isinstance(self._value, Filler):
            return self._value.fill(source, val)
        return Result.ok(self._value)


class DefaultFiller(Filler):
    """This will keep the previous value unchanged if it is
    a Result.ok. Otherwise, it will try and use a default.

    :param default: Either a predefined value or another filler to use if there was an error
    :type default: Any
    """
    def __init__(self, default: Any):
        self._filler = DependencyFiller(default)

    def fill(self, source: Source, val: Result) -> Result:
        """If the previous value is Result.err, try and use the default.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if val.is_err():
            return val.then(self._filler.fill(source, val))
        else:
            return val


class WarnFiller(Filler):
    """This filler prints the error stack contained in the
    previous result. By default, this only happens if it is a
    Result.err.

    :param level: The logging level at which to print the warnings (default: logging.WARNING)
    :type level: int
    :param logger: The logger to use for printing the warnings
    :type logger: logging.Logger|None
    :param warn_always: Always log warnings, even if the value is a Result.ok (default: False)
    :type warn_always: bool
    """

    def __init__(
        self,
        level: int = logging.WARNING,
        logger: logging.Logger|None = None,
        warn_always: bool = False
    ):
        if logger is None:
            logger = logging.getLogger("eo4eu.data")

        self._level = level
        self._logger = logger
        self._warn_always = warn_always

    def fill(self, source: Source, val: Result) -> Result:
        """Print the warnings contained in the previous result,
        leaving it unchanged.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if self._warn_always or val.is_err():
            val.log(self._logger, level = self._level)
        return val


class SourceFiller(Filler):
    """This filler tries to find the given path in its sources.
    The path parts may themselves be fillers, which will be called
    on the same source to determine the actual path.

    :param args: The path parts to look at
    :type args: List[Filler|Any]
    :param override: If set to True and the given data was found, this filler will overwrite any previous values passed to it (default: False)
    :type override: bool
    """

    def __init__(self, args: list[Filler|Any], override = False):
        self._args = [DependencyFiller(arg) for arg in args]
        self._override = override

    def _fill_iter(self, source: Source, val: Result) -> Iterator[Result]:
        for arg in self._args:
            yield arg.fill(source, val)

    def fill(self, source: Source, val: Result) -> Result:
        """Search for the configured args in the given source,
        and return the result as-is. If the previous result is a
        Result.ok and self.override is False, this will do nothing.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if val.is_ok() and not self._override:
            return val

        args = Result.merge_all(self._fill_iter(source, val))
        if args.is_err():
            return args

        result = source.get(args.get())
        if val.is_err():
            return val.then(result)

        return val.then_try(result)


class ValidateFiller(Filler):
    """This filler calls a validator function on the previous
    result. If the function returns False or raises an exception,
    a Result.err is returned.

    :param func: The validator function
    :type func: Callable[[Any],bool]
    :param name: The name of the function to use for logs
    :type name: str|None
    :param args: Extra positional arguments to pass into the function
    :type args: tuple
    :param kwargs: Extra keyword arguments to pass into the function
    :type kwargs: Dict
    """

    def __init__(
        self,
        func: Callable[[Any],bool],
        name: str|None = None,
        args: tuple|None = None,
        kwargs: dict|None = None,
    ):
        args = if_none(args, ())
        kwargs = if_none(kwargs, {})
        if name is None:
            try:
                name = func.__name__
            except Exception:
                name = "unknown"

        self._func = func
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def _err_message(self, value: Result, extra = ""):
        return f"Validator \"{self._name}\" rejected \"{value}\"{extra}"

    def fill(self, source: Source, val: Result) -> Result:
        """Return the previous result if it passes the check, otherwise
        a Result.err

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if val.is_err():
            return val.then_err(self._err_message(val))

        try:
            if self._func(val.get(), *self._args, **self._kwargs):
                return val
            return val.then_err(self._err_message(val.get()))
        except Exception as e:
            return val.then_err(self._err_message(val.get(), f": {e}"))


class ApplyFiller(Filler):
    """This filler transforms the previous result using a given function

    :param func: The function to transform the result by
    :type func: Callable[[Any],Any]
    :param name: The name of the function to use in logs
    :type name: str|None
    :param args: Extra positional arguments to pass into the function
    :type args: tuple
    :param kwargs: Extra keyword arguments to pass into the function
    :type kwargs: Dict
    :param must_apply: If True, this will return a Result.err if the function raises an exception. If False, it will simply return the previous result with an added warning (default: True)
    :type must_apply: bool
    """

    def __init__(
        self,
        func: Callable[[Any],Any],
        name: str|None = None,
        args: tuple|None = None,
        kwargs: dict|None = None,
        must_apply: bool = True,
    ):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        if name is None:
            try:
                name = func.__name__
            except Exception:
                name = "unknown"

        self._func = func
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._must_apply = must_apply

    def _err_message(self, value: Result, extra = ""):
        return f"Cannot apply function \"{self._name}\" to \"{value}\"{extra}"

    def fill(self, source: Source, val: Result) -> Result:
        """Try to apply the function to the previous result.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if val.is_err():
            return val.then_err(self._err_message(val))

        try:
            return val.then_ok(self._func(val.get(), *self._args, **self._kwargs))
        except Exception as e:
            msg = self._err_message(val, f": {e}")
            if self._must_apply:
                return val.then_err(msg)
            else:
                return val.then_warn(msg)


class CreateFiller(Filler):
    """This filler is similar to :class:`ApplyFiller`, but with some key differences:

    - It can take fillers for positional/keyword arguments
    - It always disregards the previous result

    Overall, it is meant to take a constructor for some object and
    fill it with args/kwargs fetched by other fillers.

    :param func: The constructor to call
    :type func: Callable[[Any],Any]
    :param name: The name of the constructor to use in logs
    :type name: str|None
    :param args: Positional arguments to pass into the constructor
    :type args: tuple[Filler|Any]
    :param kwargs: Keyword arguments to pass into the constructor
    :type kwargs: Dict[str,Filler|Any]
    """

    def __init__(
        self,
        func: Callable[[Any],Any],
        name: str = "unknown",
        args: tuple|None = None,
        kwargs: dict|None = None,
    ):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self._func = func
        self._name = name
        self._args = [DependencyFiller(arg) for arg in args]
        self._kwargs = [(key, DependencyFiller(arg)) for key, arg in kwargs.items()]

    def fill(self, source: Source, val: Result) -> Result:
        """Try to fetch the args/kwargs and use them to construct
        the object.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        filled_args = []
        for arg in self._args:
            filled_arg = arg.fill(source, val)
            if filled_arg.is_err():
                return filled_arg
            filled_args.append(filled_arg.get())

        filled_kwargs = {}
        for key, arg in self._kwargs:
            filled_arg = arg.fill(source, val)
            if filled_arg.is_err():
                return filled_arg
            filled_kwargs[key] = filled_arg.get()

        try:
            return val.then_ok(self._func(*filled_args, **filled_kwargs))
        except Exception as e:
            return val.then_err(f"Cannot create \"{self._name}\": {e}")


class IfElseFiller(Filler):
    """This filler checks the previous result. If it is not
    boolean, it returns Result.err. If it is True, it returns
    if_true. If it is False, it returns if_false. Both of those
    may also be fillers, in which case they will be called with
    the same source.

    :param if_true: The value/filler to use if the previous result is Result.ok(True)
    :type if_true: Filler|Any
    :param if_false: The value/filler to use if the previous result is Result.ok(False)
    :type if_false: Filler|Any
    """

    def __init__(self, if_true: Filler|Any, if_false: Filler|Any):
        self._if_true = DependencyFiller(if_true)
        self._if_false = DependencyFiller(if_false)

    def fill(self, source: Source, val: Result) -> Result:
        """Check the previous result and choose the appropriate path.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        if val.is_err():
            return val

        inner = val.get()
        if not isinstance(inner, bool):
            return val.then_err(
                f"Cannot check \"{inner}\": Is of type "
                f"\"{inner.__class__.__name__}\", expecting bool"
            )

        if inner:
            return self._if_true.fill(source, Result.none())
        else:
            return self._if_false.fill(source, Result.none())


class Try(Filler):
    """This is the most generic and user-friendly filler. It
    wraps all the default fillers defined in this module. Try
    objects should not be initialized using this constructor, but
    through one of the constructor classmethods (:func:`Try.option`,
    :func:`Try.cfgmap`, :func:`Try.secret`, :func:`Try.parent`,
    :func:`Try.create`).

    :param fillers: The fillers to chain one after another
    :type fillers: List[Filler]
    :param kwargs: This is ignored.
    """

    def __init__(self, fillers: list[Filler], **kwargs):
        self._fillers = fillers

    def fill(self, source: Source, val: Result) -> Result:
        """Run the previous result through all the fillers,
        one after another.

        :param source: The source to use
        :type source: Source
        :param val: The result of the previous filler
        :type val: eo4eu_base_utils.result.Result
        :rtype: eo4eu_base_utils.result.Result
        """
        for filler in self._fillers:
            val = filler.fill(source, val)
        return val

    def then(self, filler: Filler) -> Self:
        """Add another filler to the list. Modifies self inplace.

        :param filler: The filler to add
        :type filler: Filler
        :rtype: Try
        """
        self._fillers.append(filler)
        return self

    @classmethod
    def option(cls, *args, prefix: Any|None = None, **kwargs) -> Self:
        """Uses a :class:`eo4eu_data_utils.config.filler.SourceFiller` to search for the args in the provided sources. (NOTE: The sources are not provided here; they are meant to be given by the :class:`eo4eu_data_utils.config.ConfigBuilder` that contains this object.)

        :param args: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type args: tuple
        :param prefix: Optional path part to add to the beginning of the list
        :type prefix: Any|None
        :param kwargs: Passed to the :class:`Try` constructor
        :rtype: Try
        """
        if prefix is None:
            args = list(args)
        else:
            args = [prefix] + list(args)

        return Try([SourceFiller(args)], **kwargs)

    @classmethod
    def cfgmap(cls, *paths: str|Path) -> Self:
        """Same as :func:`Try.option`, but uses ``prefix="configmaps"``

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[str|Path]
        :rtype: Try
        """
        return cls.option(*paths, prefix = Settings.CFGMAP_PREFIX)

    @classmethod
    def secret(cls, *paths: str|Path) -> Self:
        """Same as :func:`Try.option`, but uses ``prefix="secrets"``

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[str|Path]
        :rtype: Try
        """
        return cls.option(*paths, prefix = Settings.SECRET_PREFIX)

    @classmethod
    def parent(cls, *paths: str|Path) -> Self:
        """Same as :func:`Try.option`, but uses ``prefix="__parent"``. This is
        a special prefix used by :class:`eo4eu_data_utils.config.ConfigBuilder` that
        instructs it to look into itself for values, using itself as a source. This is
        a way to base config keys on other config keys.

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[str|Path]
        :rtype: Try
        """
        return cls.option(*paths, prefix = "__parent")

    @classmethod
    def create(cls, func: Callable[[Any],Any], *args, name: str = "", **kwargs) -> Self:
        """Uses a :class:`eo4eu_data_utils.config.filler.CreateFiller` to construct
        some object given the provided constructor and args/kwargs.

        :param func: The constructor to call
        :type func: Callable[[Any],Any]
        :param args: Positional arguments to pass into the constructor
        :type args: tuple[Filler|Any]
        :param name: The name of the constructor to use in logs
        :type name: str|None
        :param kwargs: Keyword arguments to pass into the constructor
        :type kwargs: Dict[str,Filler|Any]
        :rtype: Try
        """
        return Try([CreateFiller(func, name = name, args = args, kwargs = kwargs)])

    def or_option(self, *args, prefix = None) -> Self:
        """Adds another :func:`Try.option` to this Try's list of fillers

        :param args: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type args: tuple
        :param prefix: Optional path part to add to the beginning of the list
        :type prefix: Any|None
        :rtype: Try
        """
        return self.then(Try.option(*args, prefix = prefix))

    def or_cfgmap(self, *paths: str|Path) -> Self:
        """Adds another :func:`Try.cfgmap` to this Try's list of fillers

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple
        :rtype: Try
        """
        return self.then(Try.cfgmap(*paths))

    def or_secret(self, *paths: str|Path) -> Self:
        """Adds another :func:`Try.secret` to this Try's list of fillers

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple
        :rtype: Try
        """
        return self.then(Try.secret(*paths))

    def or_parent(self, *paths: str|Path) -> Self:
        """Adds another :func:`Try.parent` to this Try's list of fillers

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple
        :rtype: Try
        """
        return self.then(Try.parent(*paths))

    def into_option(self, *args, prefix = None) -> Self:
        """Returns a :func:`Try.option`, which is called using the
        provided args with the result from this Try appended to them.
        This is for options whose path depends on the result of one
        other option.

        :param args: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type args: tuple[Filler|Any]
        :param prefix: Optional path part to add to the beginning of the list
        :type prefix: Any|None
        :rtype: Try
        """
        return Try.option(*args, self, prefix = prefix)

    def into_cfgmap(self, *paths: str|Path) -> Self:
        """Returns a :func:`Try.cfgmap`, which is called using the
        provided args with the result from this Try appended to them.
        This is for configmaps whose path depends on the result of one
        other option.

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[Filler|Any]
        :rtype: Try
        """
        return Try.cfgmap(*paths, self)

    def into_secret(self, *paths: str|Path) -> Self:
        """Returns a :func:`Try.secret`, which is called using the
        provided args with the result from this Try appended to them.
        This is for secrets whose path depends on the result of one
        other option.

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[Filler|Any]
        :rtype: Try
        """
        return Try.secret(*paths, self)

    def into_parent(self, *paths: str|Path) -> Self:
        """Returns a :func:`Try.parent`, which is called using the
        provided args with the result from this Try appended to them.
        This is for recursive options whose path depends on the result of one
        other option.

        :param paths: The path to use. This is the same path as discussed in :class:`eo4eu_data_utils.config.model.Source`.
        :type paths: tuple[Filler|Any]
        :rtype: Try
        """
        return Try.parent(*paths, self)

    def default(self, default: Filler|Any) -> Self:
        """Uses a :class:`eo4eu_data_utils.config.filler.DefaultFiller` to
        recover if previous fillers have failed.

        :param default: The default value to use. May be a filler.
        :type default: Filler|Any
        :rtype: Try
        """
        return self.then(DefaultFiller(default))

    def warn(self, **kwargs) -> Self:
        """Uses a :class:`eo4eu_data_utils.config.filler.WarnFiller` to
        warn of potential errors.

        :param kwargs: The keyword arguments to pass into the :class:`eo4eu_data_utils.config.filler.WarnFiller`
        :type kwargs: Dict
        :rtype: Try
        """
        return self.then(WarnFiller(**kwargs))

    def ifelse(self, if_true: Filler|Any, if_false: Filler|Any) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.IfElseFiller` to
        achieve basic control flow.

        :param if_true: The value/filler to use if the input is True
        :type if_true: Filler|Any
        :param if_false: The value/filler to use if the input is False
        :type if_false: Filler|Any
        :rtype: Try
        """
        return self.then(IfElseFiller(if_true, if_false))

    def validate(self, func: Callable[[Any],Any], *args, **kwargs) -> Self:
        """Uses a :class:`eo4eu_data_utils.config.filler.ValidateFiller` to
        validate its input.

        :param func: The validator function
        :type func: Callable[[Any],bool]
        :param args: Positional arguments to pass into the ValidateFiller constructor
        :type args: tuple
        :param kwargs: Keyword arguments to pass into the ValidateFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.then(ValidateFiller(func, *args, **kwargs))

    def apply(self, func: Callable[[Any],Any], *args, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        modify its input.

        :param func: The validator function
        :type func: Callable[[Any],bool]
        :param args: Positional arguments to pass into the ApplyFiller constructor
        :type args: tuple
        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.then(ApplyFiller(func, *args, **kwargs))

    def format(self, fmt_string: str, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        modify its input. Specifically, it takes the input and passes it as
        and argument to `fmt_string`.format()

        :param fmt_string: The format string, as defined in https://peps.python.org/pep-3101/
        :type fmt_string: str
        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.apply(
            func = lambda s: fmt_string.format(s),
            name = f"\"{fmt_string}\".format()",
            **kwargs
        )

    def to_int(self, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        convert its input to an integer.

        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.apply(
            func = int,
            name = "convert to int",
            **kwargs
        )

    def to_path(self, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        convert its input to a pathlib.Path.

        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.apply(
            func = Path,
            name = "convert to pathlib.Path",
            **kwargs
        )

    def to_bool(self, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        convert its input to a bool.

        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.apply(
            func = _to_bool,
            name = "convert to bool",
            **kwargs
        )

    def to_list(self, **kwargs) -> Self:
        """Uses an :class:`eo4eu_data_utils.config.filler.ApplyFiller` to
        convert its input to a list.

        :param kwargs: Keyword arguments to pass into the ApplyFiller constructor
        :type kwargs: Dict
        :rtype: Try
        """
        return self.apply(
            func = _to_list,
            name = "convert to list",
            **kwargs
        )

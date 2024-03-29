import inspect
import typing
from functools import wraps


def get_needed_methods(hint):
    return {
        m
        for b in hint.mro()
        if hasattr(b, "__abstractmethods__")
        for m in b.__abstractmethods__
    }


def quacks(o, hint) -> bool:
    needed_methods = get_needed_methods(hint)
    return all([hasattr(o, k) for k in needed_methods])


def _check_mapping_style(o, hint):
    if not quacks(o, hint):
        return False

    args = typing.get_args(hint)
    if len(args) == 0:
        return isinstance(o, hint)
    elif len(args) == 2:
        return all(
            [typecheck(k, args[0]) and typecheck(v, args[1]) for k, v in o.items()]
        )
    else:
        raise TypeError(
            f"Wrong number of parametres for {hint}; actual {len(args)}, expected 2."
        )


def _check_tuple_style(o, hint):
    args = typing.get_args(hint)
    if len(args) == 0:
        return isinstance(o, hint)
    elif len(args) == 2 and args[1] == Ellipsis:
        return all([typecheck(e, args[0]) for e in o])
    else:
        return quacks(o, hint) and all([typecheck(o[i], a) for i, a in enumerate(args)])


def _check_list_style(o, hint):
    if not quacks(o, hint):
        return False

    args = typing.get_args(hint)
    if len(args) == 0:
        return isinstance(o, hint)
    elif len(args) == 1:
        return all([typecheck(e, args[0]) for e in o])
    else:
        raise TypeError(
            f"Too many parametres for {hint}; actual {len(args)}, expected 1."
        )


def type_guard(f):
    @wraps(f)
    def inner(*a, **k):
        (bind := inspect.signature(f).bind(*a, **k)).apply_defaults()
        hints = typing.get_type_hints(f)

        if not all(
            [typecheck(bind.arguments[k], v) for k, v in hints.items() if k != "return"]
        ):
            raise TypeError()

        ret = f(*a, *k)
        if "return" in hints and not typecheck(ret, hints["return"]):
            raise TypeError()

        return ret

    return inner


def typecheck(o: typing.Any, hint=None) -> bool:
    if origin := typing.get_origin(hint):
        if origin is typing.Union:
            return any(typecheck(o, h) for h in typing.get_args(hint))
        elif issubclass(origin, typing.Mapping):
            return isinstance(o, origin) and _check_mapping_style(o, hint)
        elif issubclass(origin, typing.Sequence) or issubclass(origin, typing.Iterable):
            if origin in (tuple, typing.Tuple):
                return isinstance(o, origin) and _check_tuple_style(o, hint)
            else:
                return isinstance(o, origin) and _check_list_style(o, hint)
        else:
            return isinstance(o, origin) and quacks(o, hint)
    elif type(hint) == type and hint in (str, int, bool, bytes, list, dict, tuple, set):
        return isinstance(o, hint)
    elif hint == type(None):  # noqa
        return o is None

    try:
        hint = typing.get_type_hints(o)
        return all([typecheck(getattr(o, k), v) for k, v in hint.items()])
    except TypeError:
        return False

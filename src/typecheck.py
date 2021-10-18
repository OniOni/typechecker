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
    key_type, value_type = typing.get_args(hint)
    return all(
        [typecheck(k, key_type) and typecheck(v, value_type) for k, v in o.items()]
    )


def _check_tuple_style(o, hint):
    t = typing.get_args(hint)
    return all([typecheck(o[i], a) for i, a in enumerate(t)])


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

        assert all([typecheck(bind.arguments[k], v) for k, v in hints.items()])

        return f(*a, *k)

    return inner


def typecheck(o: typing.Any, hint=None) -> bool:
    if origin := typing.get_origin(hint):
        if origin is typing.Union:
            return any(typecheck(o, h) for h in typing.get_args(hint))
        elif issubclass(origin, typing.Mapping):
            return _check_mapping_style(o, hint)
        elif issubclass(origin, typing.Sequence) or issubclass(origin, typing.Iterable):
            if origin in (tuple, typing.Tuple):
                return _check_tuple_style(o, hint)
            else:
                return _check_list_style(o, hint)
        else:
            return quacks(o, hint)
    elif type(hint) == type and hint in (str, int, bool, bytes, list, dict):
        return isinstance(o, hint)
    elif hint == type(None):  # noqa
        return o is None

    try:
        hint = typing.get_type_hints(o)
        return all([typecheck(getattr(o, k), v) for k, v in hint.items()])
    except TypeError:
        return False

import typing


def get_needed_methods(hint):
    return {
        m
        for b in hint.mro() if hasattr(b, '__abstractmethods__')
        for m in b.__abstractmethods__
    }


def quacks(o, hint) -> bool:
    needed_methods = get_needed_methods(hint)
    return all([
        hasattr(o, k) for k in needed_methods
    ])


def _check_mapping_style(o, hint):
    key_type, value_type = hint.__args__
    return all([
        typecheck(k, key_type) and typecheck(v, value_type)
        for k, v in o.items()
    ])


def _check_tuple_style(o, hint):
    t = hint.__args__
    return all([
        typecheck(o[i], a)
        for i, a in enumerate(t)
    ])


def _check_list_style(o, hint):
    t = hint.__args__[0]
    return all([
        typecheck(e, t)
        for e in o
    ])


def typecheck(o: typing.Any, hint=None) -> bool:
    origin = typing.get_origin(hint)
    if origin:
        if origin is typing.Union:
            return any(typecheck(o, h) for h in typing.get_args(hint))
        elif issubclass(origin, typing.Mapping):
            return _check_mapping_style(o, hint)
        elif issubclass(origin, typing.MutableSequence):
            return _check_list_style(o, hint)
        elif issubclass(origin, typing.Sequence):
            return _check_tuple_style(o, hint)
    elif type(hint) == type and hint in (str, int, bool):
        return isinstance(o, hint)
    elif hint == type(None):
        return o is None

    try:
        hint = typing.get_type_hints(o)
        return all([
            typecheck(getattr(o, k), v)
            for k, v in hint.items()
        ])
    except TypeError:
        return False

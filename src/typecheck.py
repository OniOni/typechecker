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
    if hasattr(o, '__annotations__'):
        annotations = typing.get_type_hints(o)

        return all([
            typecheck(getattr(o, k), v)
            for k, v in annotations.items()
        ])
    elif type(hint) == type:
        return isinstance(o, hint)
    elif isinstance(hint, type(typing.Union)):
        return any(typecheck(o, h) for h in hint.__args__)
    else:
        has_args = False
        if hint.__args__:
            has_args = True
            if len(hint.__args__) == 2:
                typecheck_args = _check_mapping_style(o, hint) or _check_tuple_style(o, hint)
            elif len(hint.__args__) == 1:
                typecheck_args = _check_list_style(o, hint)
            else:
                typecheck_args = _check_tuple_style(o, hint)

        if hasattr(hint, '__base__'):
            instance = isinstance(o, hint.__base__)
            if has_args:
                return instance and typecheck_args
        else:
            return quacks(o, hint)

    return False



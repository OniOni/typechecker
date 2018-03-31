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
        valid(k, key_type) and valid(v, value_type)
        for k, v in o.items()
    ])


def _check_tuple_style(o, hint):
    t = hint.__args__
    return all([
        valid(o[i], a)
        for i, a in enumerate(t)
    ])


def _check_list_style(o, hint):
    t = hint.__args__[0]
    return all([
        valid(e, t)
        for e in o
    ])


def valid(o: typing.Any, hint) -> bool:
    if type(hint) == type:
        return isinstance(o, hint)
    elif isinstance(hint, type(typing.Union)):
        return any(valid(o, h) for h in hint.__args__)
    else:
        has_args = False
        if hint.__args__:
            has_args = True
            if len(hint.__args__) == 2:
                valid_args = _check_mapping_style(o, hint) or _check_tuple_style(o, hint)
            elif len(hint.__args__) == 1:
                valid_args = _check_list_style(o, hint)
            else:
                valid_args = _check_tuple_style(o, hint)

        if hasattr(hint, '__base__'):
            instance = isinstance(o, hint.__base__)
            if has_args:
                return instance and valid_args
        else:
            return quacks(o, hint)


def typecheck(obj: typing.Any) -> bool:
    annotations = typing.get_type_hints(obj)

    is_valid = {
        k: valid(getattr(obj, k), v)
        for k, v in annotations.items()
    }
    print(is_valid)
    return all(is_valid.values())

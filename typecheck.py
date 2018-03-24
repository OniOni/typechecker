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
    if hint == type(None):
        return o is None

    if type(hint) == type:
        try:
            return hint(o) == o
        except Exception:
            return False

    if hasattr(hint, '__base__'):
        return isinstance(o, hint.__base__)

    if isinstance(typing.Union, type(typing.Union)):
        a, b = hint.__args__
        return valid(o, a) or valid(o, b)

    if hint.__args__:
        if len(hint.__args__) == 2:
            return _check_mapping_style(o, hint) or _check_mapping_style(o, hint)
        elif len(hint.__args__) == 1:
            return _check_list_style(o, hint)
        else:
            return _check_tuple_style(o, hint)

    if not quacks(o, hint):
        return False


def typecheck(obj: typing.Any) -> bool:
    annotations = typing.get_type_hints(obj)

    is_valid = {
        k: valid(getattr(obj, k), v)
        for k, v in annotations.items()
    }
    print(is_valid)
    return all(is_valid.values())


class Mine:
    i: int
    c: str
    d: typing.Dict[str, int]
    l: typing.List[str]
    t: typing.Tuple[int, str, int]
    opt: typing.Optional[int]

    def __init__(self, i, c, d, l, t, opt=None):
        self.i = i
        self.c = c
        self.d = d
        self.l = l
        self.t = t
        self.opt = opt


if __name__ == '__main__':
    good = Mine(42, 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    bad = Mine('', 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    assert typecheck(good), f'{good} should be valid.'
    assert not typecheck(bad), f'{bad} should not be valid.'

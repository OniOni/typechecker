import typing


def valid(o: typing.Any, hint) -> bool:
    if type(hint) == type:
        try:
            return hint(o) == o
        except Exception:
            return False

    if type(hint) == type(typing.Union):
        a, b = hint.__args__
        return valid(o, a) or valid(o, b)

    needed_methods = {m for b in hint.mro() if hasattr(b, '__abstractmethods__') for m in b.__abstractmethods__}
    duck_typed = all([hasattr(o, k) for k in needed_methods])

    if not duck_typed:
        return False

    if hint.__args__:
        if len(hint.__args__) == 2:
            key_type, value_type = hint.__args__
            return all([
                valid(k, key_type) and valid(v, value_type)
                for k, v in o.items()
            ])
        else:
            t = hint.__args__[0]
            return all([
                valid(e, t)
                for e in o
            ])


def typecheck(obj: typing.Any) -> bool:
    annotations = typing.get_type_hints(obj)

    print({
        k: valid(getattr(obj, k), v)
        for k, v in annotations.items()
    })


class Mine:
    i: int
    c: str
    d: typing.Dict[str, int]
    l: typing.List[str]
    opt: typing.Optional[int]

    def __init__(self, i, c, d, l, opt=None):
        self.i = i
        self.c = c
        self.d = d
        self.l = l
        self.opt = opt


m = Mine(42, 'lol', {'k': 42}, ['lol'])
typecheck(m)

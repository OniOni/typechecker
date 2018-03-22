import typing


def valid(obj, hint):
    if type(hint) == type(typing.Union):
        a, b = hint.__args__
        return valid(obj, a) or valid(obj, b)
    elif type(hint) == type(typing.Collection):
        if len(hint.__args__) == 2:
            a, b = hint.__args__
            return all([
                valid(k, a) and valid(v, b)
                for k, v in obj.items()
            ])
        else:
            print(hint, obj)
            a = hint.__args__
            return all([
                valid(k, a)
                for k in obj
            ])

    return isinstance(obj, hint)


def typecheck(obj):
    annotations = typing.get_type_hints(obj)

    print(annotations)
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

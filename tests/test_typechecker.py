import typing

from typecheck import typecheck


class Mine:
    i: int
    c: str
    d: typing.Dict[str, int]
    li: typing.List[str]
    t: typing.Tuple[int, str, int]
    opt: typing.Optional[int]

    def __init__(self, i, c, d, li, t, opt=None):
        self.i = i
        self.c = c
        self.d = d
        self.li = li
        self.t = t
        self.opt = opt


def test_simple():
    good = Mine(42, 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    assert typecheck(good)


def test_bad_type():
    bad = Mine('', 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    assert not typecheck(bad)


def test_bad_args():
    bad_args = Mine('', 'lol', {'k': 42}, ['lol', 1], (1, 'l', 1))
    assert not typecheck(bad_args)


def test_nested_obj():
    class Inner:
        i: int

        def __init__(self, i):
            self.i = i

    class Outer:
        inner: Inner

        def __init__(self, inner):
            self.inner = inner

    m = Outer(Inner(42))

    assert typecheck(m)


def test_nested_obj_bad():
    class Inner:
        i: int

        def __init__(self, i):
            self.i = i

    class Outer:
        inner: Inner

        def __init__(self, inner):
            self.inner = inner

    m = Outer(42)

    assert not typecheck(m)


def test_nested_obj_bad_inner():
    class Inner:
        i: int

        def __init__(self, i):
            self.i = i

    class Outer:
        inner: Inner

        def __init__(self, inner):
            self.inner = inner

    m = Outer(Inner('lol'))

    assert not typecheck(m)

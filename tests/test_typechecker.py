import dataclasses
import typing
import pytest

from typecheck import typecheck, type_guard


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


def test_guard_bad():

    @type_guard
    def f(a: int, b: str, c: bool = False):
        return True

    with pytest.raises(AssertionError):
        f(42, 42)


def test_guard():

    @type_guard
    def f(a: int, b: str, c: bool = False):
        return True

    assert f(42, 'lol')


def test_dataclass():

    @dataclasses.dataclass
    class T:
        i: int
        s: str

    assert typecheck(T(i=42, s='lol'))
    assert not typecheck(T(i='lol', s='lol'))
    assert not typecheck(T(i=42, s=42))

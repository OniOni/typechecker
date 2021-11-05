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
    u: typing.Union[str, int]
    opt: typing.Optional[int]

    def __init__(self, i, c, d, li, t, u=42, opt=None):
        self.i = i
        self.c = c
        self.d = d
        self.li = li
        self.t = t
        self.u = u
        self.opt = opt


def test_simple():
    good = Mine(42, 'lol', {'k': 42}, ['lol'], (1, 'l', 1), 42)
    assert typecheck(good)

    good = Mine(42, 'lol', {'k': 42}, ['lol'], (1, 'l', 1), 'lol')
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

    with pytest.raises(TypeError):
        f(42, 42)


def test_guard_return_bad():

    @type_guard
    def f(a: int, b: str, c: bool = False) -> int:
        return True

    with pytest.raises(TypeError):
        f(42, 42)


def test_guard_no_return():

    @type_guard
    def f(a: int, b: str, c: bool = False):
        return True

    f(42, 'lol')


def test_guard():

    @type_guard
    def f(a: int, b: str, c: bool = False) -> bool:
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


def test_union():
    T = typing.Union[str, int]

    assert typecheck(42, T)
    assert typecheck('lol', T)
    assert not typecheck(b'lol', T)


def test_optional():
    T = typing.Optional[int]

    assert typecheck(42, T)
    assert typecheck(None, T)
    assert not typecheck('lol', T)


def test_list():
    l = [1, 2, 3]
    assert typecheck(l, typing.List[int])
    assert typecheck(l, typing.List)
    assert typecheck(l, list[int])
    assert typecheck(l, list)
    assert typecheck(l, typing.Iterable[int])
    assert typecheck(l, typing.Iterable)

    l = ["a", "b", "c"]
    assert not typecheck(l, typing.List[int])
    assert not typecheck(l, list[int])
    assert not typecheck(l, typing.Iterable[int])

    l = (1, 2, 3)
    assert not typecheck(l, typing.List[int])


def test_set():
    s = {1, 2, 3}

    assert typecheck(s, typing.Set[int])
    assert typecheck(s, typing.Set)
    assert typecheck(s, set[int])
    assert typecheck(s, set)
    assert typecheck(s, typing.Iterable[int])
    assert typecheck(s, typing.Iterable)
    assert typecheck(s, typing.Iterable[int])
    assert typecheck(s, typing.Iterable)


def test_tuple():
    t = (1, "a", True)
    assert typecheck(t, tuple[int, str, bool])
    assert typecheck(t, typing.Tuple[int, str, bool])
    assert typecheck(t, tuple)
    assert typecheck(t, typing.Tuple)
    assert not typecheck(t, tuple[int, ...])

    t = (1, 2, 3)
    assert typecheck(t, tuple[int, ...])
    assert typecheck(t, typing.Tuple[int, ...])
    assert not typecheck(t, tuple[str, ...])
    assert not typecheck(t, typing.Tuple[str, ...])

    t = [1, 2, 3]
    assert not typecheck(t, tuple[int, ...])


def test_mapping():
    m = {'k': 42}
    assert typecheck(m, dict[str, int])
    assert typecheck(m, typing.Dict[str, int])
    assert typecheck(m, typing.Mapping[str, int])
    assert typecheck(m, dict)
    assert typecheck(m, typing.Dict)
    assert typecheck(m, typing.Mapping)

import typing

from typechecker import typecheck


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


def test_simple():
    good = Mine(42, 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    bad = Mine('', 'lol', {'k': 42}, ['lol'], (1, 'l', 1))
    bad_args = Mine('', 'lol', {'k': 42}, ['lol', 1], (1, 'l', 1))

    assert typecheck(good), f'{good} should be valid.'
    assert not typecheck(bad), f'{bad} should not be valid.'
    assert not typecheck(bad_args), f'{bad_args} should not be valid.'

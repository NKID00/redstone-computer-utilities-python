from enum import Enum
from fractions import Fraction
from numbers import Rational, Real
from typing import Union


class Pos:
    '''Block position with explicit world'''
    def __init__(self, x: int, y: int, z: int, world: str) -> None:
        self.x: int = x
        self.y: int = y
        self.z: int = z
        self.world: str = world


class Vec3i:
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x: int = x
        self.y: int = y
        self.z: int = z


class Interface:
    '''Interface definition'''
    def __init__(self, name: str, lsb: Pos, increment: Vec3i, option: list[str]) -> None:
        self.name: str = name
        self.lsb: Pos = lsb
        self.increment: Vec3i = increment
        self.option: list[str] = option


class BlockUpdateType(Enum):
    NEIGHBOR_UPDATE = 'neighborUpdate'
    POST_PLACEMENT = 'postPlacement'
    ANY = 'any'


class AlarmAt(Enum):
    START = 'start'
    STOP = 'stop'


class ApiException(Exception):
    def __init__(self, code: int) -> None:
        super().__init__()
        self._code: int = code

    @property
    def code(self):
        return self._code

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, ApiException)
                and self._code == other._code)

    def __hash__(self) -> int:
        return hash((self._code,))


class ApiExceptions:
    GENERAL_ERROR = ApiException(-1)
    ARGUMENT_INVALID = ApiException(-2)
    NAME_ILLEGAL = ApiException(-3)
    NAME_EXISTS = ApiException(-4)
    NAME_NOT_FOUND = ApiException(-5)
    INTERNAL_ERROR = ApiException(-6)
    CHUNK_UNLOADED = ApiException(-7)


class Interval:
    '''Non-ambiguous interval representation.'''

    def __init__(self, interval_gametick: int, tps: Union[int, Rational] = 20):
        self._gametick = interval_gametick
        self._tps = tps

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Interval)
                and self._gametick == other._gametick)

    def __hash__(self) -> int:
        return hash((self._gametick,))

    @property
    def gametick(self) -> int:
        return self._gametick

    @property
    def redstonetick(self) -> Union[int, Rational]:
        # int is not rational to mypy :(
        interval = Fraction(self._gametick, 2)
        if interval.denominator == 1:
            return interval.numerator
        return interval

    @property
    def second(self) -> Union[int, Rational]:
        interval = Fraction(self._gametick, self._tps)
        if interval.denominator == 1:
            return interval.numerator
        return interval

    @property
    def tps(self) -> Union[int, Rational]:
        return self._tps


def gametick(interval: int, tps: Union[int, Rational] = 20) -> Interval:
    '''Non-ambiguous interval.'''
    return Interval(interval, tps)


def redstonetick(interval: Union[int, Real],
                 tps: Union[int, Rational] = 20) -> Interval:
    '''Non-ambiguous interval. Non-integral value will be floored after
    converted to gametick.'''
    return Interval(int(interval * 2), tps)


def second(interval: Union[int, Real],
           tps: Union[int, Rational] = 20) -> Interval:
    '''Non-ambiguous interval. Non-integral value will be floored after
    converted to gametick.'''
    return Interval(int(interval * tps), tps)

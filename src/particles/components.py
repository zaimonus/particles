from dataclasses import dataclass

from particles.vec import Vec


@dataclass
class Force:
    value: Vec


@dataclass
class Velocity:
    value: Vec


@dataclass
class Acceleration:
    value: Vec


@dataclass
class Position:
    value: Vec


@dataclass
class MovementHistory:
    value: list[Vec]


@dataclass
class Mass:
    value: float


@dataclass
class Age:
    value: float


@dataclass
class Brightness:
    value: float


@dataclass
class ColorShift:
    value: float

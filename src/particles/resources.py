from dataclasses import dataclass

from particles.range import Range
from particles.vec import Vec


@dataclass(slots=True)
class Time:
    value: float


@dataclass(slots=True)
class Cycles:
    value: int


@dataclass(slots=True)
class SpawningConfig:
    angle: Range
    radius: Range
    velocity_angle: Range
    mass: Range
    colorshift_angle: Range
    force: Vec
    brightness: float


@dataclass(slots=True)
class ParticleConfig:
    max_number: int
    max_age: float
    max_history: int


@dataclass(slots=True)
class BrightnessConfig:
    max_age: float
    max_history: int


@dataclass(slots=True)
class ParticleCounter:
    alive: int
    dead: int


@dataclass(slots=True)
class GravityConfig:
    position: Vec
    mass: float
    radius: float
    field_radius: float

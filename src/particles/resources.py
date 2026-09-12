from dataclasses import dataclass

from particles.vec import Vec


@dataclass
class Time:
    value: float


@dataclass
class Cycles:
    value: int


@dataclass
class ParticleConfig:
    max_number: int
    max_age: float
    max_history: int


@dataclass
class BrightnessConfig:
    max_age: float
    max_history: int


@dataclass
class ParticleCounter:
    alive: int
    dead: int


@dataclass
class GravityConfig:
    position: Vec
    mass: float
    radius: float
    field_radius: float

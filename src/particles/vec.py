from dataclasses import dataclass
from math import hypot


@dataclass
class Vec:
    x: float
    y: float

    @property
    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalize(self) -> Vec:
        m = self.magnitude
        return Vec(self.x / m, self.y / m)

    def __add__(self, other: Vec) -> Vec:
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec) -> Vec:
        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> Vec:
        return Vec(self.x * other, self.y * other)

    def __neg__(self) -> Vec:
        return Vec(-self.x, -self.y)

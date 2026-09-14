from dataclasses import dataclass


@dataclass(slots=True)
class Range:
    min: float
    max: float

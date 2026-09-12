from colorsys import hls_to_rgb
from math import cos, radians, sin, sqrt
from pathlib import Path

from svgwrite import Drawing
from svgwrite.utils import rgb

from particles.components import (
    Brightness,
    ColorShift,
    MovementHistory,
    Position,
)
from particles.ecs.annotations import Query, Resource
from particles.resources import Cycles, GravityConfig
from particles.vec import Vec


def snap_to_grid(position: Vec, grid_size: int) -> Vec:
    # world_x = grid_size * sqrt(3) * (q + r / 2)
    # world_y = grid_size * 3 / 2 * r

    # q = (sqrt(3)/3 * world_x - 1/3 * world_y) / s
    # r = (2 / 3 * world_y) / s

    x = (sqrt(3) / 3 * position.x - 1 / 3 * position.y) / grid_size
    y = (2 / 3 * position.y) / grid_size
    z = -x - y

    rx = round(x)
    ry = round(y)
    rz = round(z)

    dx = abs(rx - x)
    dy = abs(ry - y)
    dz = abs(rz - z)

    if dx >= dy and dx >= dz:
        rx = -ry - rz
    elif dy >= dz:
        ry = -rx - rz
    else:
        rz = -rx - ry

    new_x = grid_size * sqrt(3) * (rx + ry / 2)
    new_y = grid_size * 3 / 2 * ry

    return Vec(new_x, new_y)


def hexagon(position: Vec, radius: float) -> list[Vec]:
    return [
        position + Vec(cos(radians(phi + 90)) * radius, sin(radians(phi + 90)) * radius)
        for phi in (0, 60, 120, 180, 240, 300)
    ]


def to_point(vector: Vec) -> tuple[float, float]:
    return vector.x, vector.y


def to_points(vectors: list[Vec]) -> list[tuple[float, float]]:
    return [to_point(v) for v in vectors]


def hsl_to_rgb(hue: float, saturation: float, lightness: float) -> str:
    r, g, b = hls_to_rgb((hue % 360) / 360, lightness, saturation)
    return rgb(round(r * 255), round(g * 255), round(b * 255))


def draw_system(
    query: Query[Position, MovementHistory, Brightness, ColorShift],
    cycle: Resource[Cycles],
    gravity: Resource[GravityConfig],
) -> None:
    p = Path(f"./out/svgs/cycle_{cycle.value:06}.svg")
    p.parent.mkdir(parents=True, exist_ok=True)

    GRID_SIZE = 8

    dwg = Drawing(
        p, profile="tiny", size=(1600, 900), viewBox="-800 -450 1600 900", debug=False
    )

    for _, position, path, brightness, color_shift in query:
        size = GRID_SIZE
        distance_to_gravity = (gravity.position - position.value).magnitude
        brightness_form_distance = (1000 - min(1000, distance_to_gravity)) / 1000
        total_brightness = brightness.value * brightness_form_distance

        pos = snap_to_grid(position.value, GRID_SIZE)
        points = to_points(hexagon(pos, size))

        dwg.add(
            dwg.polygon(
                points,
                fill="black",
                stroke=hsl_to_rgb(color_shift.value, 1.0, total_brightness),
            )
        )

        path_len = len(path.value)
        for i, point in enumerate(path.value):
            p = snap_to_grid(point, GRID_SIZE)
            factor = size * i / path_len
            points = to_points(hexagon(p, factor))
            dwg.add(
                dwg.polygon(
                    points,
                    fill="black",
                    stroke=hsl_to_rgb(color_shift.value, 0.9, total_brightness / 2),
                )
            )

    dwg.add(
        dwg.polygon(
            to_points(hexagon(gravity.position, gravity.radius)),
            fill="black",
            stroke=hsl_to_rgb(0, 1.0, 0.9),
            stroke_width="3px",
        )
    )

    dwg.save(pretty=True)

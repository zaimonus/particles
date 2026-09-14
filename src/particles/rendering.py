from colorsys import hls_to_rgb
from dataclasses import dataclass
from math import cos, radians, sin, sqrt

import pygame

from particles.vec import Vec


@dataclass
class Camera:
    position: Vec
    zoom: float
    viewPort: Vec

    def zoom_to(self, zoom: float):
        self.zoom = min(max(0.02, zoom), 100)

    def world_to_screen(self, pos: Vec) -> Vec:
        return (self.viewPort * 0.5) + (self.position + pos) * self.zoom


@dataclass(frozen=True)
class RenderContext:
    surface: pygame.Surface
    camera: Camera


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


def to_world_points(vectors: list[Vec], camera: Camera) -> list[tuple[float, float]]:
    return [to_point(camera.world_to_screen(vector)) for vector in vectors]


def hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
    r, g, b = hls_to_rgb((hue % 360) / 360, lightness, saturation)
    return round(r * 255), round(g * 255), round(b * 255)

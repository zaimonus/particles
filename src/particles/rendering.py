from colorsys import hls_to_rgb
from dataclasses import dataclass
from math import cos, radians, sin, sqrt

import pygame

from particles.components import (
    Brightness,
    ColorShift,
    MovementHistory,
    Position,
)
from particles.ecs.annotations import Query, Resource
from particles.resources import GravityConfig
from particles.vec import Vec


@dataclass
class Camera:
    x: float
    y: float
    zoom: float

    @property
    def pos(self) -> Vec:
        return Vec(self.x, self.y)

    def zoom_to(self, zoom: float):
        self.zoom = min(max(0.02, zoom), 100)

    def world_to_screen(self, pos: Vec) -> Vec:
        return self.pos + pos * self.zoom


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


def render_system(
    query: Query[Position, MovementHistory, Brightness, ColorShift],
    render_context: Resource[RenderContext],
    gravity: Resource[GravityConfig],
) -> None:
    GRID_SIZE = 8

    for _, position, path, brightness, color_shift in query:
        size = GRID_SIZE
        distance_to_gravity = (gravity.position - position.value).magnitude

        # brightness_form_distance = (1000 - min(1000, distance_to_gravity)) / 1000
        total_brightness = brightness.value# * brightness_form_distance

        pos = snap_to_grid(position.value, GRID_SIZE)
        points = hexagon(pos, size)
        world_points = to_world_points(points, render_context.camera)

        pygame.draw.polygon(
            render_context.surface,
            color=pygame.color.Color(
                *hsl_to_rgb(color_shift.value, 1.0, total_brightness)
            ),
            points=world_points,
        )

        path_len = len(path.value)
        for i, point in enumerate(path.value):
            p = snap_to_grid(point, GRID_SIZE)
            factor = size * i / path_len
            points = hexagon(p, factor)
            world_points = to_world_points(points, render_context.camera)
            pygame.draw.polygon(
                render_context.surface,
                color=pygame.color.Color(
                    *hsl_to_rgb(color_shift.value, 0.9, total_brightness / 2)
                ),
                points=world_points,
            )

    pygame.draw.polygon(
        render_context.surface,
        color=pygame.color.Color(*hsl_to_rgb(0, 1.0, 0.9)),
        points=to_world_points(
            hexagon(gravity.position, gravity.radius), render_context.camera
        ),
    )

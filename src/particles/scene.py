from dataclasses import dataclass
from typing import cast

import pygame
from pygame.event import Event

from particles.components import Brightness, ColorShift, MovementHistory, Position
from particles.ecs.world import World
from particles.rendering import (
    Camera,
    RenderContext,
    hexagon,
    hsl_to_rgb,
    snap_to_grid,
    to_world_points,
)
from particles.resources import GravityConfig, ParticleConfig
from particles.world import tick


@dataclass
class Control:
    key: str
    desc: str

WHITE = 255, 255, 255

class Scene:
    def __init__(self, camera: Camera, world: World) -> None:
        self.grid_size = 8
        self.camera = camera
        self.world = world
        self.font = pygame.font.Font(None, 24)

        self.speed = 1.0

        self.gravity = self.world.resources.require(GravityConfig)
        self.particles = self.world.resources.require(ParticleConfig)

        self.controls = [
            Control("arrow right", "Increase particle limit"),
            Control("arrow left", "Decrease particle limit"),
            Control("arrow up", "Increase gravity mass"),
            Control("arrow down", "Decrease gravity mass"),
            Control("w", "Move up"),
            Control("a", "Move left"),
            Control("d", "Move right"),
            Control("s", "Move down"),
            Control("x", "Zoom in"),
            Control("y", "Zoom out"),
            Control("n", "Invert gravity mass"),
            Control("+", "Speed up"),
            Control("-", "Slow down"),
            Control("q", "Exit"),
        ]

    def update(self, dt: float):
        tick(self.world, dt * self.speed)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.camera.position.y += 500 * dt
        if keys[pygame.K_s]:
            self.camera.position.y -= 500 * dt
        if keys[pygame.K_a]:
            self.camera.position.x += 500 * dt
        if keys[pygame.K_d]:
            self.camera.position.x -= 500 * dt

        if keys[pygame.K_x]:
            self.camera.zoom_to(self.camera.zoom + dt)
        if keys[pygame.K_y]:
            self.camera.zoom_to(self.camera.zoom - dt)

        if keys[pygame.K_PLUS]:
            self.speed += 0.5
        if keys[pygame.K_MINUS]:
            self.speed -= 0.5

        if keys[pygame.K_LEFT]:
            self.particles.max_number = max(self.particles.max_number - 10, 0)
        if keys[pygame.K_RIGHT]:
            self.particles.max_number += 10

        if keys[pygame.K_UP]:
            self.gravity.mass *= 2
        if keys[pygame.K_DOWN]:
            self.gravity.mass = max(self.gravity.mass / 2, 1)

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            self.gravity.mass = -self.gravity.mass

    def render(self, context: RenderContext):
        surface = context.surface
        camera = context.camera
        query = self.world.query(Position, MovementHistory, Brightness, ColorShift)

        surface.fill((0, 0, 0))

        for _, position, path, brightness, color_shift in query:
            position = cast(Position, position)
            path = cast(MovementHistory, path)
            brightness = cast(Brightness, brightness)
            color_shift = cast(ColorShift, color_shift)

            snapped_position = snap_to_grid(position.value, self.grid_size)

            points = hexagon(snapped_position, self.grid_size)
            world_points = to_world_points(points, camera)

            pygame.draw.polygon(
                surface,
                color=pygame.color.Color(
                    *hsl_to_rgb(color_shift.value, 1.0, brightness.value)
                ),
                points=world_points,
            )

            path_len = len(path.value)
            for i, point in enumerate(path.value):
                p = snap_to_grid(point, self.grid_size)
                factor = self.grid_size * i / path_len
                points = hexagon(p, factor)
                world_points = to_world_points(points, camera)
                pygame.draw.polygon(
                    surface,
                    color=pygame.color.Color(
                        *hsl_to_rgb(color_shift.value, 0.9, brightness.value / 2)
                    ),
                    points=world_points,
                )

        pygame.draw.polygon(
            surface,
            color=pygame.color.Color(*hsl_to_rgb(0, 1.0, 0.9)),
            points=to_world_points(
                hexagon(self.gravity.position, self.gravity.radius), camera
            ),
        )
        
        longest_dest = max(len(c.desc) for c in self.controls)
        width = self.font.size(longest_dest * 2 * ' ')[0]
        separator = self.font.render("-> ", False, WHITE)
        for i, control in enumerate(self.controls):
            desc = self.font.render(control.desc, False, WHITE)
            key = self.font.render(control.key, False, WHITE)
            
            y = self.camera.viewPort.y - (i + 1) * self.font.get_height()
            surface.blit(desc, (0, y))
            surface.blit(separator, (width, y))
            surface.blit(key, (width + separator.get_width(), y))

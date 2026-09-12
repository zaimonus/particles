import pygame

from particles.components import Brightness, ColorShift, MovementHistory, Position
from particles.rendering import Camera, RenderContext, render_system
from particles.resources import GravityConfig, ParticleConfig
from particles.world import tick, world

# def main() -> None:
#     FPS = 60
#     DURATION = 30  # in seconds
#     SPEED = 1

#     frames = FPS * DURATION
#     time_per_frame = SPEED / FPS

#     print("[System] Starting simulation.")
#     for i in range(1, frames + 1):
#         print(f"[Info] Frame: {i}/{frames}", end="\r")
#         tick(world, time_per_frame)
#         draw_system(world.query(Position, MovementHistory, Brightness, ColorShift), world.resources.require(Cycles))
#     print()
#     print("[System] Done.")


def main() -> None:
    FPS = 60
    FIXED_TICK = 1 / 30

    WIDTH = 1920
    HEIGHT = 1080
    SIZE = WIDTH, HEIGHT

    pygame.init()
    screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True

    camera = Camera(WIDTH // 2, HEIGHT // 2, 0.75)
    context = RenderContext(screen, camera)
    accumulated = 0
    dt = 0
    time = 1
    
    gravity = world.resources.require(GravityConfig)
    particles = world.resources.require(ParticleConfig)
    n_countdown = 0.2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        accumulated += min(dt, 0.25)
        while accumulated >= FIXED_TICK:
            tick(world, FIXED_TICK * time)
            accumulated -= FIXED_TICK

        screen.fill((0, 0, 0))
        render_system(
            world.query(Position, MovementHistory, Brightness, ColorShift),
            context,
            world.resources.require(GravityConfig),
        )

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            camera.y += 300 * dt
        if keys[pygame.K_s]:
            camera.y -= 300 * dt
        if keys[pygame.K_a]:
            camera.x += 300 * dt
        if keys[pygame.K_d]:
            camera.x -= 300 * dt

        if keys[pygame.K_x]:
            camera.zoom_to(camera.zoom + dt)
        if keys[pygame.K_y]:
            camera.zoom_to(camera.zoom - dt)

        if keys[pygame.K_PLUS]:
            time += 0.5
        if keys[pygame.K_MINUS]:
            time -= 0.5

        if keys[pygame.K_LEFT]:
            particles.max_number = max(particles.max_number - 10, 0)
        if keys[pygame.K_RIGHT]:
            particles.max_number += 10

        if keys[pygame.K_UP]:
            gravity.mass *= 2
        if keys[pygame.K_DOWN]:
            gravity.mass = max(gravity.mass / 2, 1)
        if keys[pygame.K_n] and n_countdown < 0:
            gravity.mass = -gravity.mass
            n_countdown = 0.2
        n_countdown -= dt

        if keys[pygame.K_q]:
            running = False

        pygame.display.flip()
        dt = clock.tick(FPS) / 1000

    pygame.quit()

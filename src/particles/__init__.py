import pygame

from particles.rendering import Camera, RenderContext
from particles.scene import Scene
from particles.vec import Vec
from particles.world import init_world


def main() -> None:
    FPS = 60
    FIXED_TICK = 1 / 30

    WIDTH = 1920
    HEIGHT = 1080
    SIZE = WIDTH, HEIGHT

    pygame.init()
    screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    camera = Camera(
        Vec(0, 0),
        0.75,
        Vec(WIDTH, HEIGHT),
    )
    context = RenderContext(screen, camera)
    running = True

    accumulated = 0
    dt = 0

    scene = Scene(camera, init_world())

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                running = False
            else:
                scene.handle_event(event)

        accumulated += min(dt, 0.25)
        while accumulated >= FIXED_TICK:
            scene.update(FIXED_TICK)
            accumulated -= FIXED_TICK

        scene.render(context)

        pygame.display.flip()
        dt = clock.tick(FPS) / 1000

    pygame.quit()

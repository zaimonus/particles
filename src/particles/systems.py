from math import cos, radians, sin
from random import uniform

from particles.components import (
    Age,
    Brightness,
    ColorShift,
    Force,
    Mass,
    MovementHistory,
    Position,
    Velocity,
)
from particles.ecs.annotations import Mutable, Query, Resource
from particles.ecs.commands import Commands
from particles.resources import (
    Cycles,
    GravityConfig,
    ParticleConfig,
    ParticleCounter,
    Time,
)
from particles.vec import Vec


def time_system(time: Resource[Mutable[Time]], dt: float) -> None:
    time.value += dt


def cycles_system(cycles: Resource[Mutable[Cycles]]) -> None:
    cycles.value += 1


def aging_system(
    query: Query[Mutable[Age]],
    counter: Resource[Mutable[ParticleCounter]],
    config: Resource[ParticleConfig],
    commands: Commands,
    dt: float,
) -> None:
    for entity, age in query:
        age.value += abs(dt)
        if age.value > config.max_age:
            commands.despawn(entity)
            counter.alive -= 1
            counter.dead += 1


def brightness_system(
    query: Query[Age, Mutable[Brightness]], config: Resource[ParticleConfig]
) -> None:
    for _, age, brightness in query:
        normalized = age.value / config.max_age * 2
        brightness.value = -(0.5 * (normalized - 1) ** 2) + 1


def spawn_system(
    counter: Resource[Mutable[ParticleCounter]],
    config: Resource[ParticleConfig],
    commands: Commands,
) -> None:
    i = 0
    while counter.alive < config.max_number:
        angle = radians(uniform(0, 360))
        radius = uniform(750, 1250)
        x = cos(angle) * radius
        y = sin(angle) * radius

        va = radians(uniform(2, 60)) + angle
        vx = cos(va) * radius
        vy = sin(va) * radius
        dx = vx - x
        dy = vy - y

        commands.spawn(
            Position(Vec(x, y)),
            MovementHistory([]),
            Velocity(Vec(dx, dy)),
            Force(Vec(0, 0)),
            Mass(uniform(5, 100)),
            Age(i),
            Brightness(0),
            ColorShift(uniform(280, 320)),
        )

        i += 1
        counter.alive += 1


def force_reset_system(query: Query[Mutable[Force]]) -> None:
    for _, force in query:
        force.value.x = 0
        force.value.y = 0


def gravity_force_system(
    query: Query[Position, Mass, Mutable[Force]], gravity: Resource[GravityConfig]
) -> None:
    for _, position, mass, force in query:
        direction: Vec = gravity.position - position.value
        distance = direction.magnitude
        f = 1 * mass.value * gravity.mass / (distance**2)
        force.value += direction.normalize() * f


def moving_system(
    query: Query[
        Mutable[Position], Mutable[Velocity], Mutable[MovementHistory], Force, Mass
    ],
    config: Resource[ParticleConfig],
    dt: float,
) -> None:
    for _, position, velocity, history, force, mass in query:
        acceleration = force.value * (1 / mass.value)
        velocity.value += acceleration * dt

        history.value.append(position.value)
        history.value = history.value[-config.max_history :]
        position.value += velocity.value * dt


def death_system(
    query: Query[Position],
    gravity: Resource[GravityConfig],
    counter: Resource[Mutable[ParticleCounter]],
    commands: Commands,
) -> None:
    for entity, position in query:
        distance = (gravity.position - position.value).magnitude
        if distance < gravity.radius:
            commands.despawn(entity)
            counter.alive -= 1
            counter.dead += 1

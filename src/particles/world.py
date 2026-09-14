from particles.components import (
    Age,
    Brightness,
    Force,
    Mass,
    MovementHistory,
    Position,
    Velocity,
)
from particles.ecs.commands import Commands, Invoker
from particles.ecs.world import World
from particles.range import Range
from particles.resources import (
    Cycles,
    GravityConfig,
    ParticleConfig,
    ParticleCounter,
    SpawningConfig,
    Time,
)
from particles.systems import (
    aging_system,
    brightness_system,
    cycles_system,
    death_system,
    force_reset_system,
    gravity_force_system,
    moving_system,
    spawn_system,
    time_system,
)
from particles.vec import Vec

world = World()
world.resources.add(GravityConfig(Vec(0, 0), 10_000_000.0, 100, 5000))
world.resources.add(Time(0))
world.resources.add(Cycles(0))
world.resources.add(ParticleCounter(0, 0))
world.resources.add(ParticleConfig(30, 20, 10))


def tick(world: World, dt: float):
    # Spawn new particles
    commands = Commands()
    spawn_system(
        counter=world.resources.require(ParticleCounter),
        particle_config=world.resources.require(ParticleConfig),
        spawn_config=world.resources.require(SpawningConfig),
        commands=commands,
    )
    Invoker(world).apply(commands)

    time_system(
        world.resources.require(Time),
        dt,
    )
    cycles_system(
        world.resources.require(Cycles),
    )
    force_reset_system(
        world.query(Force),
    )
    gravity_force_system(
        world.query(Position, Mass, Force),
        world.resources.require(GravityConfig),
    )
    moving_system(
        world.query(Position, Velocity, MovementHistory, Force, Mass),
        world.resources.require(ParticleConfig),
        dt,
    )

    # Despawn some particles
    commands = Commands()
    aging_system(
        world.query(Age),
        world.resources.require(ParticleCounter),
        world.resources.require(ParticleConfig),
        commands,
        dt,
    )
    Invoker(world).apply(commands)

    brightness_system(
        world.query(Age, Brightness), world.resources.require(ParticleConfig)
    )

    commands = Commands()
    death_system(
        world.query(Position),
        world.resources.require(GravityConfig),
        world.resources.require(ParticleCounter),
        commands,
    )
    Invoker(world).apply(commands)

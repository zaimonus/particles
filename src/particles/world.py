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
    death_by_distance_system,
    force_reset_system,
    gravity_force_system,
    moving_system,
    spawn_system,
    time_system,
)
from particles.vec import Vec


def init_world() -> World:
    world = World()

    world.resources.add(
        resource=GravityConfig(
            position=Vec(x=0, y=0),
            mass=10_000_000.0,
            radius=100,
            field_radius=5000,
        )
    )
    world.resources.add(
        resource=Time(
            value=0,
        )
    )
    world.resources.add(
        resource=Cycles(
            value=0,
        )
    )
    world.resources.add(
        resource=ParticleCounter(
            alive=0,
            dead=0,
        )
    )
    world.resources.add(
        resource=ParticleConfig(
            max_number=30,
            max_age=20,
            max_history=10,
        )
    )
    world.resources.add(
        resource=SpawningConfig(
            angle=Range(min=0, max=360),
            radius=Range(min=750, max=1250),
            velocity_angle=Range(min=2, max=60),
            mass=Range(min=5, max=100),
            colorshift_angle=Range(min=280, max=320),
            force=Vec(x=0, y=0),
            brightness=0,
        )
    )

    return world


def tick(world: World, dt: float):
    commands = Commands()

    spawn_system(
        counter=world.resources.require(ParticleCounter),
        particle_config=world.resources.require(ParticleConfig),
        spawn_config=world.resources.require(SpawningConfig),
        commands=commands,
    )

    time_system(
        time=world.resources.require(Time),
        dt=dt,
    )

    cycles_system(
        cycles=world.resources.require(Cycles),
    )

    force_reset_system(
        query=world.query(Force),
    )

    gravity_force_system(
        query=world.query(Position, Mass, Force),
        gravity=world.resources.require(GravityConfig),
    )

    moving_system(
        query=world.query(Position, Velocity, MovementHistory, Force, Mass),
        config=world.resources.require(ParticleConfig),
        dt=dt,
    )

    aging_system(
        query=world.query(Age),
        counter=world.resources.require(ParticleCounter),
        config=world.resources.require(ParticleConfig),
        commands=commands,
        dt=dt,
    )

    brightness_system(
        query=world.query(Age, Brightness),
        config=world.resources.require(ParticleConfig),
    )

    death_by_distance_system(
        query=world.query(Position),
        gravity=world.resources.require(GravityConfig),
        counter=world.resources.require(ParticleCounter),
        commands=commands,
    )

    Invoker(world).apply(commands)

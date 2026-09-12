from dataclasses import dataclass, field
from functools import singledispatchmethod
from typing import Any

from particles.ecs.entity import Entity
from particles.ecs.world import World


@dataclass(frozen=True, slots=True)
class Command:
    pass


@dataclass(frozen=True, slots=True)
class SpawnCommand(Command):
    components: tuple[Any]


@dataclass(frozen=True, slots=True)
class DespawnCommand(Command):
    entity: Entity


@dataclass(frozen=True, slots=True)
class AddCommand(Command):
    entity: Entity
    component: Any


@dataclass(frozen=True, slots=True)
class ReplaceCommand(Command):
    entity: Entity
    component: Any


@dataclass(frozen=True, slots=True)
class RemoveCommand(Command):
    entity: Entity
    type_: type[Any]


@dataclass
class Commands:
    _commands: list[Command] = field(default_factory=list)

    def spawn(self, *components: Any) -> None:
        self._commands.append(SpawnCommand(components))

    def despawn(self, entity: Entity) -> None:
        self._commands.append(DespawnCommand(entity))

    def add(self, entity: Entity, component: Any) -> None:
        self._commands.append(AddCommand(entity, component))

    def replace(self, entity: Entity, component: Any) -> None:
        self._commands.append(ReplaceCommand(entity, component))

    def remove(self, entity: Entity, type_: type[Any]) -> None:
        self._commands.append(RemoveCommand(entity, type_))


@dataclass
class Invoker:
    world: World

    def apply(self, commands: Commands) -> None:
        for command in commands._commands:
            self._apply_single(command)

    @singledispatchmethod
    def _apply_single(self, command: Command) -> None:
        raise NotImplementedError

    @_apply_single.register
    def _(self, command: SpawnCommand) -> None:
        self.world.spawn(*command.components)

    @_apply_single.register
    def _(self, command: DespawnCommand) -> None:
        self.world.despawn(command.entity)

    @_apply_single.register
    def _(self, command: AddCommand) -> None:
        self.world.components.store(type(command.component)).insert(
            command.entity, command.component
        )

    @_apply_single.register
    def _(self, command: ReplaceCommand) -> None:
        self.world.components.store(type(command.component)).replace(
            command.entity, command.component
        )

    @_apply_single.register
    def _(self, command: RemoveCommand) -> None:
        self.world.components.store(command.type_).remove(command.entity)

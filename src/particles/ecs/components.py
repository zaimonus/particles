from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from particles.ecs.entity import Entity


@dataclass
class ComponentStore[T]:
    _components: dict[Entity, T] = field(default_factory=dict)

    def get(self, entity: Entity) -> T:
        return self._components[entity]

    def try_get(self, entity: Entity) -> T | None:
        return self._components.get(entity, None)

    def insert(self, entity: Entity, component: T) -> None:
        self._components[entity] = component

    def replace(self, entity: Entity, component: T) -> None:
        self._components[entity] = component

    def remove(self, entity: Entity) -> T:
        return self._components.pop(entity)

    def contains(self, entity: Entity) -> bool:
        return entity in self._components

    def entities(self) -> Iterable[Entity]:
        return self._components.keys()

    def values(self) -> Iterable[T]:
        return self._components.values()

    def items(self) -> Iterable[tuple[Entity, T]]:
        return self._components.items()

    def __len__(self) -> int:
        return len(self._components)


@dataclass
class ComponentRegistry:
    _stores: dict[type[Any], ComponentStore[Any]] = field(default_factory=dict)

    def store[T](self, type_: type[T]) -> ComponentStore[T]:
        return self._stores.setdefault(type_, ComponentStore[T]())

    def has[T](self, entity: Entity, type_: type[T]) -> bool:
        return self.store(type_).contains(entity)

    def stores(self) -> Iterable[ComponentStore[Any]]:
        return self._stores.values()

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid7

from particles.ecs.components import ComponentRegistry
from particles.ecs.entity import Entity
from particles.ecs.resources import ResourceRegistry


@dataclass
class World:
    _entities: list[Entity] = field(default_factory=list)
    components: ComponentRegistry = field(default_factory=ComponentRegistry)
    resources: ResourceRegistry = field(default_factory=ResourceRegistry)

    def spawn[*Ts](self, *components: *Ts) -> Entity:
        entity = int(uuid7())
        self._entities.append(entity)
        for component in components:
            self.components.store(type(component)).insert(entity, component)
        return entity

    def despawn(self, entity: Entity) -> None:
        for store in self.components.stores():
            if store.contains(entity):
                store.remove(entity)
        self._entities.remove(entity)

    def is_alive(self, entity: Entity) -> bool:
        return entity in self._entities

    def query(self, *types: type[object]) -> Iterator[tuple[Entity, *tuple[Any, ...]]]:
        stores = [self.components.store(component_type) for component_type in types]

        primary_store = min(stores, key=lambda store: len(store._components))

        for entity in primary_store._components:
            components: list[Any] = []
            matches = True

            for store in stores:
                component: Any = store.get(entity)

                if component is None:
                    matches = False
                    break

                components.append(component)

            if matches:
                yield (entity, *components)

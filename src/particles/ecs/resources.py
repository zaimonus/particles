from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResourceRegistry:
    _resources: dict[type[Any], Any] = field(default_factory=dict)

    def add[T](self, resource: T) -> None:
        if type(resource) in self._resources:
            raise ValueError(f"Resource already registered: {type(resource)!r}")
        self._resources[type(resource)] = resource

    def get[T](self, type_: type[T]) -> T | None:
        return self._resources.get(type_, None)

    def require[T](self, type_: type[T]) -> T:
        return self._resources[type_]

    def remove[T](self, type_: type[T]) -> T:
        return self._resources.pop(type_)

    def has[T](self, type_: type[T]) -> bool:
        return type_ in self._resources

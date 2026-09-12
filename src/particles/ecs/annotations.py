from collections.abc import Iterator
from typing import Annotated

from particles.ecs.entity import Entity


class ResourceMarker:
    pass


type Resource[T] = Annotated[T, ResourceMarker()]


class QueryMarker:
    pass


type Query[*Ts] = Annotated[Iterator[tuple[Entity, *Ts]], QueryMarker()]


class MutableMarker:
    pass


type Mutable[T] = Annotated[T, MutableMarker()]

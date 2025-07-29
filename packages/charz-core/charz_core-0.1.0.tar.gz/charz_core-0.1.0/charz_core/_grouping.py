from __future__ import annotations

import sys
from enum import unique
from functools import wraps
from typing import TYPE_CHECKING, Callable, Any

from ._annotations import T, GroupID

if TYPE_CHECKING:
    from ._node import Node


# NOTE: Variants of the enum produces the same hash as if it was using normal `str`
if sys.version_info >= (3, 11):
    from enum import StrEnum, auto

    @unique
    class Group(StrEnum):
        """Enum for core node groups used in `charz-core`."""

        NODE = auto()

else:
    from enum import Enum

    @unique
    class Group(str, Enum):
        """Enum for core node groups used in `charz-core`."""

        NODE = "node"


def group(group_id: GroupID, /) -> Callable[[type[T]], type[T]]:
    """Adds a `node`/`component` to the given `group`.

    This works by wrapping `__new__` and `_free`.
    Recommended types for parameter `group_id`: `LiteralString`, `StrEnum` or `int`.
    `NOTE`: Each node is added to the current scene's group when `__new__` is called.

    Args:
        group_id (GroupID): *Hashable* object used for group ID

    Returns:
        Callable[[type[T]], type[T]]: Wrapped class
    """
    # NOTE: Lazyloading `Scene`
    # Do import here to prevent cycling dependencies,
    # as there won't be a lot of scene creation
    from ._scene import Scene

    def wrapper(kind: type[T]) -> type[T]:
        original_new = kind.__new__

        @wraps(original_new)
        def new_wrapper(cls: type[T], *args: Any, **kwargs: Any) -> T:
            instance = original_new(cls, *args, **kwargs)
            Scene.current.groups[group_id][instance.uid] = instance  # type: ignore
            return instance

        kind.__new__ = new_wrapper

        if (original_free := getattr(kind, "_free", None)) is not None:

            @wraps(original_free)
            def free_wrapper(this: Node) -> None:
                if original_free is not None:
                    original_free(this)
                del Scene.current.groups[group_id][this.uid]

            kind._free = free_wrapper  # type: ignore
        else:

            def free(this: Node) -> None:
                del Scene.current.groups[group_id][this.uid]

            free.__name__ = "_free"
            kind._free = free  # type: ignore
        return kind

    return wrapper

from __future__ import annotations

from typing import TypeVar, TypeAlias, Generic, Callable

T = TypeVar("T")
Priority: TypeAlias = int
FrameTask: TypeAlias = Callable[[T], None]


class FrameTaskManager(Generic[T], dict[Priority, FrameTask[T]]):
    """A dict-like manager that auto-sorts tasks by priority.

    `NOTE` The higher the priority, the earlier the task will be executed.
    """

    def __setitem__(self, key: Priority, value: FrameTask[T]) -> None:
        super().__setitem__(key, value)
        sorted_items = sorted(self.items(), reverse=True)
        self.clear()
        self.update(sorted_items)

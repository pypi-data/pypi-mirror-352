"""
Charz Core
==========

Core logic for `charz`

Includes
--------

- Annotations
  - `Self`  (from standard `typing` or from package `typing-extensions`)
- Math (from package `linflex`)
  - `lerp`
  - `sign`
  - `clamp`
  - `move_toward`
  - `Vec2`
  - `Vec2i`
  - `Vec3`
- Framework
  - `Engine`
  - `Scene`
- Decorators
  - `group`
- Enums
  - `Group`
- Components
  - `TransformComponent`
- Nodes
  - `Camera`
  - `Node`
  - `Node2D`
"""

__all__ = [
    "Engine",
    "Camera",
    "Scene",
    "group",
    "Group",
    "Node",
    "Self",
    "Node2D",
    "TransformComponent",
    "lerp",
    "sign",
    "clamp",
    "move_toward",
    "Vec2",
    "Vec2i",
    "Vec3",
]

# Re-exports
import sys as _sys

if _sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from linflex import lerp, sign, clamp, move_toward, Vec2, Vec2i, Vec3

# Exports
from ._engine import Engine
from ._camera import Camera
from ._scene import Scene
from ._grouping import Group, group
from ._node import Node
from ._components._transform import TransformComponent
from ._prefabs._node2d import Node2D

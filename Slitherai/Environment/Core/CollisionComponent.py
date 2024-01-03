import sys
from typing import List

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import pyray as pr

from Slitherai.Environment.Core.Component import Component


class CollisionComponent(Component):
    collision_type: int

    def __init__(self):
        super().__init__()
        self.bodies: List[pr.Vector2]
        self.radius: float
        self.is_static: bool = True

    def on_collision(self, index: int, other: Self, other_index: int):
        _ = index, other, other_index
        pass

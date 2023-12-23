from Slitherai.Environment.Core.Component import Component
import pyray as pr
from typing import List, Self


class CollisionComponent(Component):
    def __init__(
        self, bodies: List[pr.Vector2] = [], radius: float = 0, is_static: bool = True
    ):
        super().__init__()
        self.bodies = bodies
        self.radius = radius
        self.is_static = is_static

    def on_collision(self, index: int, other: Self, other_index: int):
        pass

    def render(self):
        for body in self.bodies:
            pr.draw_circle_v(body, self.radius, pr.Color(255, 0, 0, 255))


from collections import deque
import pyray as pr
import numpy as np
from Slitherai.Environment.Core.Component import Component


class SnakeBodyComponent(Component):
    def __init__(
        self, length: int, head_location: pr.Vector2, direction: pr.Vector2
    ) -> None:
        self.length: int = length

        self.center = head_location
        self.direction = pr.vector2_normalize(direction)
        self.direction = pr.vector2_scale(self.direction, 2)

        self.body: deque[pr.Vector2] = deque(
            [
                pr.Vector2(
                    self.center.x + self.direction.x * -i,
                    self.center.y + self.direction.y * -i,
                )
                for i in range(length)
            ]
        )

        self.radius = 10

        self.color = pr.Color(0, 0, 0, 255)

        self.max_turn = 2.74
        self.count = 0

    def update(self, delta_time: float) -> None:
        self.count += 1
        self.head = self.body[0]
        self.pointer = pr.get_mouse_position()
        self.pointer_dir = pr.vector2_normalize(
            pr.vector2_subtract(self.pointer, self.head)
        )

        self.pointed_angle = (
            np.arctan2(self.pointer_dir.y, self.pointer_dir.x) + np.pi / 2
        )

        self.direction_angle = (
            np.arctan2(self.direction.y, self.direction.x) + np.pi / 2
        )

        self.angle = self.pointed_angle - self.direction_angle
        self.angle = self.angle if self.angle < np.pi else self.angle - np.pi * 2

        self.angle = pr.clamp(
            self.angle, -self.max_turn * delta_time, self.max_turn * delta_time
        )

        self.direction = pr.vector2_rotate(self.direction, self.angle)

        self.body.appendleft(pr.vector2_add(self.head, self.direction))
        self.body.pop()

        if self.count >= 60:
            self.grow()
            self.count = 0

    def render(self) -> None:
        for part in self.body:
            pr.draw_circle_v(part, self.radius, self.color)

    def grow(self) -> None:
        self.body.append(self.body[-1])


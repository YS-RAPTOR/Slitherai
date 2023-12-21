import pyray as pr
import numpy as np
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Constants import (
    MAX_LENGTH,
    MIN_BOOST_MASS,
    BOOST_SPEED_CONSTANT,
    SPEED_CONSTANT,
    MAX_TURN,
    BOOST_TURN,
)
from typing import List


class SnakeBodyComponent(Component):
    def __init__(self, head_location: pr.Vector2, start_direction: pr.Vector2) -> None:
        self.radius = 20
        self.direction = pr.vector2_normalize(start_direction)
        self.input_dir = self.direction
        self.is_boosting = False

        self.body: List[pr.Vector2] = [
            pr.Vector2(
                head_location.x + self.direction.x * -i * (self.length() / 2),
                head_location.y + self.direction.y * -i * (self.length() / 2),
            )
            for i in range(self.length())
        ]

        self.color = pr.Color(0, 0, 0, 255)

    def can_boost(self) -> bool:
        return self.is_boosting and self.radius > MIN_BOOST_MASS

    def speed(self) -> float:
        if self.can_boost():
            return BOOST_SPEED_CONSTANT
        return self.length() * SPEED_CONSTANT

    def max_turn(self) -> float:
        if self.can_boost():
            return BOOST_TURN
        return MAX_TURN

    def length(self) -> int:
        return int(pr.clamp(self.radius / 2, 1, MAX_LENGTH))

    def set_controls(self, W, S, A, D, Space):
        x = 0
        y = 0

        if W:
            y = -1
        elif S:
            y = 1

        if D:
            x = 1
        elif A:
            x = -1

        self.is_boosting = Space

        if x == 0 and y == 0:
            return

        self.input_dir = pr.vector2_normalize(pr.Vector2(x, y))

    def update(self, delta_time: float) -> None:
        # Get Direction
        input_angle = np.arctan2(self.input_dir.y, self.input_dir.x) + np.pi / 2

        direction_angle = np.arctan2(self.direction.y, self.direction.x) + np.pi / 2

        angle = input_angle - direction_angle
        angle = angle if angle < np.pi else angle - np.pi * 2

        max_turn = self.max_turn()
        angle = pr.clamp(angle, -max_turn, max_turn)

        self.direction = pr.vector2_rotate(self.direction, angle)

        self.body[0] = pr.vector2_add(
            pr.vector2_scale(self.direction, self.speed() * delta_time),
            self.body[0],
        )

        if self.can_boost():
            self.shrink(0.5)

        for i in range(1, self.length()):
            dir = pr.vector2_normalize(
                pr.vector2_subtract(self.body[i - 1], self.body[i])
            )
            self.body[i] = pr.vector2_subtract(
                self.body[i - 1], pr.vector2_scale(dir, self.length() / 2)
            )

    def render(self) -> None:
        for part in self.body:
            pr.draw_circle_v(part, self.radius, self.color)

        pr.draw_circle_v(self.body[0], self.radius, pr.Color(255, 0, 0, 255))

        pr.draw_text(
            f"{self.speed()}",
            10,
            10,
            20,
            pr.Color(0, 0, 0, 255),
        )

    def grow(self, mass: float) -> None:
        self.radius += mass
        if self.length() > len(self.body):
            dir = pr.vector2_normalize(
                pr.vector2_subtract(self.body[-2], self.body[-1])
            )
            self.body.append(
                pr.vector2_subtract(
                    self.body[-1], pr.vector2_scale(dir, self.length() / 2)
                )
            )

    def shrink(self, mass: float) -> None:
        self.radius -= mass
        if self.length() < len(self.body):
            self.body.pop()


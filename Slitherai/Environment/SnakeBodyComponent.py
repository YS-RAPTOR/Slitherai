from typing import List, Self

import numpy as np
import pyray as pr

from Slitherai.Environment.Constants import (
    BOOST_DROP_RATE,
    BOOST_SHRINK_RATE,
    BOOST_SPEED_CONSTANT,
    BOOST_TURN,
    DEATH_DROP_RATE,
    DEATH_MASS_RANGE,
    MASS_TO_RADIUS,
    MAX_LENGTH,
    MAX_TURN,
    MIN_BOOST_RADIUS,
    SPEED_CONSTANT,
)
from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Event import Event
from Slitherai.Environment.Food import Food, FoodSpawner


class ServerSnakeBodyComponent(CollisionComponent):
    def __init__(
        self,
        head_location: pr.Vector2,
        start_direction: pr.Vector2,
        id: int,
        food_spawner: FoodSpawner,
    ) -> None:
        self.radius = 20
        self.id = id
        self.direction = pr.vector2_normalize(start_direction)
        self.input_dir = self.direction
        self.is_boosting = False
        self.is_static = False
        self.food_spawner = food_spawner
        if self.food_spawner is None:
            raise Exception("FoodSpawner not found")

        self.bodies: List[pr.Vector2] = [
            pr.Vector2(
                head_location.x + self.direction.x * -i * (self.length() / 2),
                head_location.y + self.direction.y * -i * (self.length() / 2),
            )
            for i in range(self.length())
        ]

        self.color = pr.Color(128, 128, 128, 255)

    def init(self):
        entity = self.get_entity()
        world = entity.get_world()
        self.size = world.size
        self.boost_food = 0

    def can_boost(self) -> bool:
        return self.is_boosting and self.radius > MIN_BOOST_RADIUS

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

    def killed(self):
        # TODO : EVENT
        food_mass = int((self.radius / MASS_TO_RADIUS) * DEATH_DROP_RATE)

        while food_mass > 0:
            food_mass -= self.food_spawner.spawn_food(
                self.bodies[0], 50, DEATH_MASS_RANGE
            )

        entity = self.get_entity()
        world = entity.get_world()
        world.queue_entity_removal(entity)

    def EatingEvent(self, mass: float) -> None:
        entity = self.get_entity()
        world = entity.get_world()
        event = Event(0, EntityThatAte=self.id, MassEaten=mass)
        world.produce_event(event)

    def KilledEvent(self, other: Self | None) -> None:
        entity = self.get_entity()
        world = entity.get_world()
        if other is None:
            killedEvent = Event(1, EntityKilled=self.id, KilledBy=None)
            world.produce_event(killedEvent)
        else:
            killedEvent = Event(1, EntityKilled=self.id, KilledBy=other.id)
            killEvent = Event(2, EntityThatKilled=other.id, KilledEntity=self.id)

    def on_collision(self, index: int, other: CollisionComponent, other_index: int):
        # Head is colliding
        if index == 0:
            # Head is colliding with food
            if other.collision_type == Food.collision_type:
                mass = other.eat()  # type: ignore
                self.EatingEvent(mass)
                self.grow(mass)
            # Head is colliding with Body
            elif other.collision_type == self.collision_type:
                self.KilledEvent(other)  # type: ignore
                self.killed()
        # Body is colliding
        else:
            # Body is colliding with food
            if other.collision_type == Food.collision_type:
                mass = other.eat()  # type: ignore
                self.EatingEvent(mass)
                self.grow(mass)

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
        if angle < 0:
            angle += np.pi * 2
        angle = angle if angle < np.pi else angle - np.pi * 2

        max_turn = self.max_turn()
        angle = pr.clamp(angle, -max_turn, max_turn)

        self.direction = pr.vector2_rotate(self.direction, angle * delta_time)

        self.bodies[0] = pr.vector2_add(
            pr.vector2_scale(self.direction, self.speed() * delta_time),
            self.bodies[0],
        )

        if self.can_boost():
            self.shrink(BOOST_SHRINK_RATE * delta_time)
            self.boost_food += BOOST_SHRINK_RATE * BOOST_DROP_RATE * delta_time
            if self.boost_food >= 1:
                self.boost_food -= 1
                loc_dir = pr.vector2_normalize(
                    pr.vector2_subtract(self.bodies[-2], self.bodies[-1])
                )
                loc = pr.vector2_subtract(
                    self.bodies[-1], pr.vector2_scale(loc_dir, self.radius * 1.5)
                )
                self.food_spawner.spawn_food(loc, 1)

        for i in range(1, self.length()):
            dir = pr.vector2_normalize(
                pr.vector2_subtract(self.bodies[i - 1], self.bodies[i])
            )
            self.bodies[i] = pr.vector2_subtract(
                self.bodies[i - 1], pr.vector2_scale(dir, self.length() / 2)
            )

        # Check if out of bounds
        if (
            self.bodies[0].x < 0
            or self.bodies[0].x > self.size
            or self.bodies[0].y < 0
            or self.bodies[0].y > self.size
        ):
            self.KilledEvent(None)
            self.killed()

    def draw(self, camera: pr.Camera2D) -> None:
        for part in self.bodies:
            pr.draw_circle_v(part, self.radius, self.color)

        pr.draw_circle_v(self.bodies[0], self.radius, pr.Color(255, 0, 0, 255))

    def grow(self, mass: float) -> None:
        self.radius += mass * MASS_TO_RADIUS
        if self.length() > len(self.bodies):
            dir = pr.vector2_normalize(
                pr.vector2_subtract(self.bodies[-2], self.bodies[-1])
            )
            self.bodies.append(
                pr.vector2_subtract(
                    self.bodies[-1], pr.vector2_scale(dir, self.length() / 2)
                )
            )

    def shrink(self, mass: float) -> None:
        self.radius -= mass * MASS_TO_RADIUS
        if self.length() < len(self.bodies):
            self.bodies.pop()


class ClientSnakeBodyComponent(Component):
    def __init__(
        self, is_player: bool, radius: float, bodies: List[pr.Vector2]
    ) -> None:
        self.is_player = is_player
        self.radius = radius
        self.bodies = bodies

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True

    def shrink(self, mass: float) -> None:
        self.radius -= mass * MASS_TO_RADIUS
        if self.length() < len(self.bodies):
            self.bodies.pop()

    def length(self) -> int:
        return int(pr.clamp(self.radius / 2, 1, MAX_LENGTH))

    def draw(self, camera: pr.Camera2D):
        for part in self.bodies[1:]:
            pr.draw_circle_v(part, self.radius, pr.Color(128, 128, 128, 255))
        pr.draw_circle_v(self.bodies[0], self.radius, pr.Color(255, 0, 0, 255))

    def can_boost(self) -> bool:
        return (
            pr.is_key_down(pr.KeyboardKey.KEY_SPACE) and self.radius > MIN_BOOST_RADIUS
        )

    def update(self, delta_time: float):
        if self.is_player:
            x = 0
            y = 0

            if pr.is_key_down(pr.KeyboardKey.KEY_W):
                y = -1
            elif pr.is_key_down(pr.KeyboardKey.KEY_S):
                y = 1

            if pr.is_key_down(pr.KeyboardKey.KEY_D):
                x = 1
            elif pr.is_key_down(pr.KeyboardKey.KEY_A):
                x = -1

            if x == 0 and y == 0:
                self.optimistic_update(delta_time)

            input_angle = np.arctan2(y, x) + np.pi / 2
            direction = pr.vector2_subtract(self.bodies[0], self.bodies[1])
            direction_angle = np.arctan2(direction.y, direction.x) + np.pi / 2
            speed = BOOST_SPEED_CONSTANT if self.can_boost() else SPEED_CONSTANT
            angle = input_angle - direction_angle
            if angle < 0:
                angle += np.pi * 2
            angle = angle if angle < np.pi else angle - np.pi * 2

            max_turn = BOOST_TURN if self.can_boost() else MAX_TURN
            angle = pr.clamp(angle, -max_turn, max_turn)

            direction = pr.vector2_rotate(direction, angle * delta_time)

            self.bodies[0] = pr.vector2_add(
                pr.vector2_scale(direction, speed * delta_time),
                self.bodies[0],
            )

            for i in range(1, len(self.bodies)):
                dir = pr.vector2_normalize(
                    pr.vector2_subtract(self.bodies[i - 1], self.bodies[i])
                )
                self.bodies[i] = pr.vector2_subtract(
                    self.bodies[i - 1], pr.vector2_scale(dir, len(self.bodies) / 2)
                )
            if self.can_boost():
                self.shrink(BOOST_SHRINK_RATE * delta_time)

        else:
            self.optimistic_update(delta_time)

    def optimistic_update(self, delta_time: float):
        direction = pr.vector2_subtract(self.bodies[0], self.bodies[1])

        self.bodies[0] = pr.vector2_add(
            pr.vector2_scale(direction, SPEED_CONSTANT * delta_time),
            self.bodies[0],
        )

        for i in range(1, len(self.bodies)):
            dir = pr.vector2_normalize(
                pr.vector2_subtract(self.bodies[i - 1], self.bodies[i])
            )
            self.bodies[i] = pr.vector2_subtract(
                self.bodies[i - 1], pr.vector2_scale(dir, len(self.bodies) / 2)
            )


class SnakeStatsComponent(Component):
    def __init__(self, snake: ClientSnakeBodyComponent) -> None:
        self.stats_location = pr.Vector2(10, 10)
        self.snake = snake

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True

    def draw(self, camera: pr.Camera2D):
        boost_text = (
            "Can Boost"
            if self.snake.radius > MIN_BOOST_RADIUS
            else f"Mass Remaining: {round((MIN_BOOST_RADIUS-self.snake.radius)/MASS_TO_RADIUS)}"
        )
        boost_text += "\nBOOSTING" if self.snake.can_boost() else "\nNOT BOOSTING"
        player_pos = pr.vector2_add_value(self.snake.bodies[0], 0)
        pr.draw_text_ex(
            pr.get_font_default(),
            f"Position: {round(player_pos.x)}, {round(player_pos.y)}\nMass: {round(self.snake.radius/MASS_TO_RADIUS)}\n{boost_text}",
            self.stats_location,
            20,
            1,
            pr.Color(128, 128, 128, 255),
        )


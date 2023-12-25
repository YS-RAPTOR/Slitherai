import numpy as np
import pyray as pr

from Slitherai.Environment.Constants import (
    FOOD_DO_SOMETHING_EVERY,
    FOOD_MAX_MASS,
    INITIAL_FOOD_SPAWN,
    IS_DEBUG,
    OPTIMAL_RESOLUTION_WIDTH,
    SPAWN_FOOD_AREA,
)
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld


class Food(CollisionComponent):
    def __init__(
        self,
        location: pr.Vector2,
        can_grow: bool = True,
        mass: int = 1,
        radius: float = 10,
        do_render: bool = True,
    ) -> None:
        super().__init__()
        self.bodies = [location]
        self.radius = radius
        self.color = pr.Color(0, 255, 0, 255)
        self.mass = mass
        self.can_grow = can_grow
        self.do_render = do_render

    def grow(self):
        if self.mass < FOOD_MAX_MASS and self.can_grow:
            self.mass += 1
            self.radius += 1

    def can_render(self, camera: pr.Camera2D) -> bool:
        return self.do_render and pr.check_collision_point_circle(
            self.bodies[0], camera.target, OPTIMAL_RESOLUTION_WIDTH
        )

    def eat(self):
        entity: Entity = self.get_entity()
        world: GridWorld = entity.get_world()
        world.queue_entity_removal(entity)
        # TODO : EVENT
        return self.mass

    def render(self, camera: pr.Camera2D):
        pr.draw_circle_v(self.bodies[0], self.radius, self.color)


class FoodSpawner(Component):
    def __init__(self, app: Application) -> None:
        super().__init__()
        self.app = app
        self.random = np.random.default_rng()

    def init(self):
        world: GridWorld = self.app.worlds[self.app.active_world]  # type: ignore
        self.size = world.size
        for _ in range(INITIAL_FOOD_SPAWN):
            x = self.random.integers(0, world.size)
            y = self.random.integers(0, world.size)
            world.add_entity(
                Entity("Food", [Food(pr.Vector2(x, y), do_render=IS_DEBUG)])
            )

    def update(self, delta_time: float) -> None:
        random = self.random.random()

        if random >= delta_time / FOOD_DO_SOMETHING_EVERY:
            return

        length = len(self.app.worlds[self.app.active_world].entities)
        random_entity = self.random.integers(0, length)
        entity = self.app.worlds[self.app.active_world].entities[random_entity]
        food: Food = entity.get_component(Food.component_id)  # type: ignore
        if food is None:
            return
        if self.random.random() < 0.5:
            x = self.random.integers(
                food.bodies[0].x - SPAWN_FOOD_AREA,
                food.bodies[0].x + SPAWN_FOOD_AREA,
            )
            y = self.random.integers(
                food.bodies[0].y - SPAWN_FOOD_AREA,
                food.bodies[0].y + SPAWN_FOOD_AREA,
            )
            xClamped = np.clip(x, 0, self.size)
            yClamped = np.clip(y, 0, self.size)
            self.app.worlds[self.app.active_world].add_entity(
                Entity(
                    "Food",
                    [Food(pr.Vector2(xClamped, yClamped), do_render=IS_DEBUG)],
                )
            )
        else:
            food.grow()


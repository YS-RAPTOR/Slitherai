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
        do_draw: bool = True,
    ) -> None:
        super().__init__()
        self.bodies = [location]
        self.radius = radius
        self.color = pr.Color(0, 255, 0, 255)
        self.mass = mass
        self.can_grow = can_grow
        self.do_draw = do_draw

    def grow(self):
        if self.mass < FOOD_MAX_MASS and self.can_grow:
            self.mass += 1
            self.radius += 1

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return self.do_draw and pr.check_collision_point_circle(
            self.bodies[0], camera.target, OPTIMAL_RESOLUTION_WIDTH
        )

    def eat(self):
        entity: Entity = self.get_entity()
        world: GridWorld = entity.get_world()
        world.queue_entity_removal(entity)
        return self.mass

    def draw(self, camera: pr.Camera2D):
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
                Entity("Food", [Food(pr.Vector2(x, y), do_draw=IS_DEBUG)])
            )

    def spawn_food(
        self, location: pr.Vector2, radius: float = SPAWN_FOOD_AREA, mass_range=[1, 2]
    ) -> int:
        x = self.random.integers(
            location.x - radius,
            location.x + radius,
        )
        y = self.random.integers(
            location.y - radius,
            location.y + radius,
        )
        xClamped = np.clip(x, 0, self.size)
        yClamped = np.clip(y, 0, self.size)

        mass = self.random.integers(mass_range[0], mass_range[1])
        self.app.worlds[self.app.active_world].add_entity(
            Entity(
                "Food",
                [Food(pr.Vector2(xClamped, yClamped), mass=mass, do_draw=IS_DEBUG)],
            )
        )
        return mass

    def update(self, delta_time: float) -> None:
        random = self.random.random()

        if random >= delta_time / FOOD_DO_SOMETHING_EVERY:
            return

        length = len(self.app.worlds[self.app.active_world].entities)
        random_entity = self.random.integers(0, length)
        entity = self.app.worlds[self.app.active_world].entities[random_entity]
        food: Food = entity.get_component(Food.component_id)  # type: ignore
        if food is None or food.collision_type != Food.collision_type:
            return
        if self.random.random() < 0.5:
            self.spawn_food(food.bodies[0])
        else:
            food.grow()


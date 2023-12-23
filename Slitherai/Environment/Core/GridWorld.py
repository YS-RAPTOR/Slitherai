from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
from Slitherai.Environment.Core.World import World
import pyray as pr
from radyx import GridPhysics


class GridWorld(World):
    def __init__(self, size: int, block_size: int, camera: pr.Camera2D):
        super().__init__()
        self.grid_size = size // block_size
        self.size = self.grid_size * block_size
        self.block_size = block_size

        self.grid = GridPhysics(self.size, self.block_size)
        self.camera = camera

    def update(self, delta_time: float):
        self.grid.reset()
        for i, entity in enumerate(self.entities):
            collision_comp: CollisionComponent = entity.get_component(
                CollisionComponent.component_id
            )
            if collision_comp is None:
                continue
            # Most Likely Food
            if collision_comp.is_static and len(collision_comp.bodies) == 1:
                self.grid.add_static_circle(
                    i, collision_comp.bodies[0], collision_comp.radius
                )
            elif not collision_comp.is_static and len(collision_comp.bodies) >= 1:
                self.grid.add_dynamic_circles(
                    i, collision_comp.bodies, collision_comp.radius
                )

        collisions = self.grid.get_collisions()
        for collision in collisions:
            self_entity: CollisionComponent = self.entities[
                collision.self_entity_index
            ].get_component(CollisionComponent.component_id)

            other_entity: CollisionComponent = self.entities[
                collision.other_entity_index
            ].get_component(CollisionComponent.component_id)

            self_entity.on_collision(
                collision.self_body_index, other_entity, collision.other_body_index
            )
        super().update(delta_time)

    def render(self):
        pr.draw_grid(
            self.grid_size,
            self.block_size,
        )


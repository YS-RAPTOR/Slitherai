import pyray as pr
from radyx import GridPhysics

from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
from Slitherai.Environment.Core.World import World


class GridWorld(World):
    def __init__(self, size: int, block_size: int):
        super().__init__()
        self.grid_size = size // block_size
        self.size = self.grid_size * block_size
        self.block_size = block_size

        self.grid = GridPhysics(self.size, self.block_size)
        self.fps_pos = pr.Vector2(10, 10)

    def update(self, delta_time: float):
        self.grid.reset()
        for i, entity in enumerate(self.entities):
            collision_comp: CollisionComponent = entity.get_component(  # type: ignore
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
            try:
                self_entity: CollisionComponent = self.entities[  # type: ignore
                    collision.self_entity_index
                ].get_component(CollisionComponent.component_id)

                other_entity: CollisionComponent = self.entities[  # type: ignore
                    collision.other_entity_index
                ].get_component(CollisionComponent.component_id)

                self_entity.on_collision(
                    collision.self_body_index, other_entity, collision.other_body_index
                )
            except IndexError:
                print("Collision Information")
                for i in collisions:
                    print(
                        f"Self Entity Index: {i.self_entity_index} | Other Entity Index: {i.other_entity_index} | Self Body Index: {i.self_body_index} | Other Body Index: {i.other_body_index}"
                    )

                print("Entity Information")
                for i, entity in enumerate(self.entities):
                    print(f"{i} : {entity}")

                ids = self.grid.get_collisions_within_area(
                    pr.Vector2(25000, 25000), 25000
                )
                print("Grid Probe")
                for i in ids:
                    try:
                        print(f"{i} : {self.entities[i]}")
                    except IndexError:
                        print(f"{i} : None")

                raise IndexError

        super().update(delta_time)

    def render(self, camera: pr.Camera2D):
        pr.draw_grid(
            self.grid_size,
            self.block_size,
        )
        world_pos = pr.get_screen_to_world_2d(self.fps_pos, camera)
        pr.draw_fps(int(world_pos.x), int(world_pos.y))
        super().render(camera)


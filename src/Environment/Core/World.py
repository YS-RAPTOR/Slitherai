from Environment.Core.Entity import Entity
from typing import List


# Stores all the entities in the game.
class World:
    def __init__(self) -> None:
        self.entities: List[Entity] = []

    def add_entity(self, entity: Entity) -> Entity:
        self.entities.append(entity)
        return entity

    def remove_entity(self, entity: Entity):
        self.entities.remove(entity)

    def get_entity(self, entity_name: str) -> Entity | None:
        for entity in self.entities:
            if entity.name == entity_name:
                return entity
        return None

    def update_start(self):
        for entity in self.entities:
            entity.update_start()

    def update(self, delta_time: float):
        for entity in self.entities:
            entity.update(delta_time)

    def update_end(self):
        for entity in self.entities:
            entity.update_end()

    def fixed_update_start(self):
        for entity in self.entities:
            entity.fixed_update_start()

    def fixed_update(self, fixed_delta_time: float):
        for entity in self.entities:
            entity.fixed_update(fixed_delta_time)

    def fixed_update_end(self):
        for entity in self.entities:
            entity.fixed_update_end()


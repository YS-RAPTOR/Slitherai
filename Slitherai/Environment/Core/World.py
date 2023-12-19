from typing import List
from Slitherai.Environment.Core.Entity import Entity


class World:
    def __init__(self):
        self.entities: List[Entity] = []
        self.is_active: bool = False

    def add_entity(self, entity: Entity):
        if self.is_active:
            entity.init()
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        if self.is_active:
            entity.destroy()
        self.entities.remove(entity)

    def init(self):
        self.is_active = True
        for entity in self.entities:
            entity.init()

    def destroy(self):
        self.is_active = False
        for entity in self.entities:
            entity.destroy()

    def update(self, delta_time: float):
        for entity in self.entities:
            if entity.is_active:
                entity.update(delta_time)

    def render(self):
        for entity in self.entities:
            if entity.is_active:
                entity.render()


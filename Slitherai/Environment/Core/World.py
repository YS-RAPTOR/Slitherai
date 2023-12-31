from collections import deque
from typing import List

import pyray as pr

from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.Event import Event


class World:
    def __init__(self):
        self.entities: List[Entity] = []
        self.ui_entities: List[Entity] = []
        self.is_active: bool = False
        self.to_delete: List[Entity] = []
        self.events = deque()

    def get_world(self):
        return self

    def produce_event(self, event: Event):
        self.events.append(event)

    def consume_event(self):
        if len(self.events) == 0:
            return None
        return self.events.popleft()

    def add_entity(self, entity: Entity):
        if self.is_active:
            entity.init_callbacks(self.get_world)
            entity.init()
        self.entities.append(entity)

    def add_ui_entity(self, entity: Entity):
        if self.is_active:
            entity.init_callbacks(self.get_world)
            entity.init()
        self.ui_entities.append(entity)

    def remove_entity(self, entity: Entity):
        if self.is_active:
            entity.destroy()
        self.entities.remove(entity)

    def remove_ui_entity(self, entity: Entity):
        if self.is_active:
            entity.destroy()
        self.ui_entities.remove(entity)

    def queue_entity_removal(self, entity: Entity):
        self.to_delete.append(entity)

    def init(self):
        self.is_active = True
        for entity in self.entities:
            entity.init_callbacks(self.get_world)
            entity.init()

        for entity in self.ui_entities:
            entity.init_callbacks(self.get_world)
            entity.init()

    def destroy(self):
        self.is_active = False
        for entity in self.entities:
            entity.destroy()

        for entity in self.ui_entities:
            entity.destroy()

    def update(self, delta_time: float):
        for entity in self.entities:
            if entity.is_active & entity.can_update:
                entity.update(delta_time)

        for entity in self.ui_entities:
            if entity.is_active & entity.can_update:
                entity.update(delta_time)

        for entity in self.to_delete:
            self.remove_entity(entity)
        self.to_delete.clear()

    def draw(self, camera: pr.Camera2D):
        for entity in self.entities:
            if entity.is_active and entity.can_draw:
                entity.draw(camera)

    def ui_draw(self, camera):
        for entity in self.ui_entities:
            if entity.is_active and entity.can_draw:
                entity.draw(camera)


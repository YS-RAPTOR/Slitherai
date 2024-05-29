from typing import List

import pyray as pr

from Slitherai.Environment.Core.Component import Component


class Entity:
    def __init__(self, name: str, components: List[Component]):
        self.name: str = name
        self.components: List[Component] = components
        self.is_active: bool = True
        self.can_update: bool = True
        self.can_draw: bool = True
        for component in components:
            component.init_callbacks(self.get_component, self.get_name, self.get_entity)

    def init_callbacks(self, get_world):
        self.get_world = get_world

    def init(self):
        for component in self.components:
            component.init()

    def destroy(self):
        for component in self.components:
            component.destroy()

    def get_entity(self):
        return self

    def add_component(self, component: Component):
        self.components.append(component)
        component.init_callbacks(self.get_component, self.get_name, self.get_entity)
        component.init()

    def get_name(self):
        return self.name

    def get_component(self, component_type: int):
        for component in self.components:
            if component.component_id == component_type:
                return component
        return None

    def remove_component(self, component: Component):
        self.components.remove(component)

    def update(self, delta_time: float):
        for component in self.components:
            component.update(delta_time)

    def draw(self, camera: pr.Camera2D):
        for component in self.components:
            if component.can_draw(camera):
                component.draw(camera)


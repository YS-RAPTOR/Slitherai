from Slitherai.Environment.Core.Component import Component
from typing import List


class Entity:
    def __init__(self, name: str, components: List[Component]):
        self.name: str = name
        self.components: List[Component] = components
        self.is_active: bool = True
        for component in components:
            component.init_callbacks(self.get_component)

    def __del__(self):
        for component in self.components:
            component.destroy()

    def init(self):
        for component in self.components:
            component.init()

    def destroy(self):
        for component in self.components:
            component.destroy()

    def add_component(self, component: Component):
        self.components.append(component)
        component.init_callbacks(self.get_component)
        component.init()

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

    def render(self):
        for component in self.components:
            if component.can_render:
                component.render()


from typing import List, Self
from Environment.Core.Component import Component


class Entity:
    def __init__(self, name: str = "Entity", components: List[Component] = []):
        self.name: str = name
        self._components: List[Component] = components

        for component in self._components:
            component.init(self.get_component)

    def __del__(self):
        for component in self._components:
            component.destroy()

    def add_component(self, component: Component) -> Self:
        self._components.append(component)
        component.init(self.get_component)
        return self

    def remove_component(self, component: Component):
        self._components.remove(component)
        component.destroy()

    def get_component(self, component_id: int) -> Component | None:
        for component in self._components:
            if component.component_id == component_id:
                return component
        return None

    def update_start(self):
        for component in self._components:
            if not component.can_update:
                continue
            component.update_start()

    def update(self, delta_time: float):
        for component in self._components:
            if not component.can_update:
                continue
            component.update(delta_time)

    def update_end(self):
        for component in self._components:
            if not component.can_update:
                continue
            component.update_end()


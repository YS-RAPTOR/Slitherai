from typing import Callable


class ComponentId(type):
    _id_counter = 0

    def __new__(cls, name, bases, dct):
        dct["component_id"] = cls._id_counter
        cls._id_counter += 1
        return super().__new__(cls, name, bases, dct)


class Component(metaclass=ComponentId):
    component_id: int
    can_update: bool = True

    def __init__(self) -> None:
        super().__init__()

    def init(self, get_component: Callable):
        """Runs once when the component is added to an entity"""
        self.get_entity_component = get_component
        return

    def destroy(self):
        """Runs once when the component is removed from an entity"""
        return

    def update_start(self):
        """Runs before the first update"""
        return

    def update(self, delta_time: float):
        """Runs every frame"""
        return

    def update_end(self):
        """Runs after the last update"""
        return


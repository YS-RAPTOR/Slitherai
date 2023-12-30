from typing import Callable

import pyray as pr


class Component_Id(type):
    _id_counter = 0
    _collision_type = 0

    def __new__(cls, name, bases, dct):
        # Assign a unique integer ID to the subclass

        # print type of parameter
        if "Collision" in bases.__str__():
            dct["collision_type"] = cls._collision_type
            cls._collision_type += 1
            return super().__new__(cls, name, bases, dct)

        dct["component_id"] = cls._id_counter
        cls._id_counter += 1

        return super().__new__(cls, name, bases, dct)


class Component(metaclass=Component_Id):
    component_id: int

    def init_callbacks(
        self, get_component: Callable, get_name: Callable, get_entity: Callable
    ):
        self.get_component = get_component
        self.get_name = get_name
        self.get_entity = get_entity

    def init(self):
        pass

    def destroy(self):
        pass

    def update(self, delta_time: float):
        pass

    def draw(self, camera: pr.Camera2D):
        pass

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True

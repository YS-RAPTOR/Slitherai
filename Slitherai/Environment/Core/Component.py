from typing import Callable


class Component_Id(type):
    _id_counter = 0

    def __new__(cls, name, bases, dct):
        # Assign a unique integer ID to the subclass
        dct["component_id"] = cls._id_counter
        cls._id_counter += 1
        return super().__new__(cls, name, bases, dct)


class Component(metaclass=Component_Id):
    component_id: int
    can_render: bool = True

    def init_callbacks(self, get_component: Callable):
        self.get_component = get_component

    def init(self):
        pass

    def destroy(self):
        pass

    def update(self, delta_time: float):
        pass

    def render(self):
        pass


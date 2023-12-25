from typing import List, Tuple
from pyray import Vector2

class Player:
    def __init__(self) -> None:
        self.id: int
        self.radius: float
        self.position: List[Tuple[float, float]]

class Food:
    def __init__(self) -> None:
        self.id: int
        self.radius: float
        self.position: Tuple[float, float]

class Replicator:
    def __init__(self) -> None:
        self.players: List[Player]
        self.foods: List[Food]

    def clear(self) -> None:
        pass

    def add_player(self, id: int, radius: float, position: List[Vector2]) -> None:
        pass

    def add_food(self, id: int, radius: float, position: Vector2) -> None:
        pass

    def encode(self) -> bytes:
        pass

    def decode(self, buffer: bytes) -> None:
        pass


from Environment.Core.Component import Component
from collections import deque

class SnakeBody:
    def __init__(self) -> None:
        super().__init__()
        self.bodies = deque()

    def resize(self, size: int):
        self.bodies.

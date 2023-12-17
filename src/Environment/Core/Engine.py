from Environment.Core.World import World
from Environment.Core.Renderer import Renderer


# Singleton Engine class
class Engine:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Engine, cls).__new__(cls)
        return cls.instance

    def __init__(self, fps: int = 60):
        self.fps = fps
        self.world = World()
        self.renderer = Renderer()

    def run(self):
        while True:
            self.world.update_start()
            self.world.update(1 / self.fps)
            self.world.update_end()


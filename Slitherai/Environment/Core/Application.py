import pyray as pr
from typing import List
from Slitherai.Environment.Core.World import World


# Create a singleton instance of the application
class Application:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, title: str, fps: int):
        self.title: str = title
        self.fps: int = fps
        self.time = 1 / fps

        pr.init_window(0, 0, self.title)
        pr.set_target_fps(fps)
        self.running: bool = True
        self.worlds: List[World] = []
        self.active_world: int = -1

    def __del__(self):
        pr.close_window()

    def add_world(self, world: World):
        self.worlds.append(world)

    def set_active_world(self, World: int):
        if (len(self.worlds) - 1) < World:
            return False
        self.worlds[self.active_world].destroy()
        self.active_world = World
        self.worlds[self.active_world].init()
        return True

    def update(self):
        self.running = not pr.window_should_close()
        self.worlds[self.active_world].update(self.time)

    def render(self):
        pr.begin_drawing()
        pr.clear_background(pr.Color(255, 255, 255, 255))
        self.worlds[self.active_world].render()
        pr.end_drawing()

    def run(self):
        if self.active_world == -1:
            raise ValueError("No active world set")
        while self.running:
            self.update()
            self.render()


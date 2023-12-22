import pyray as pr
from typing import List
from Slitherai.Environment.Core.World import World


# Create a singleton instance of the application
class Application:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, title: str = "", fps: int = 0):
        if title == "" or fps == 0:
            return

        self.title: str = title
        self.fps: int = fps
        self.time = 1 / self.fps
        self.width = 0
        self.height = 0

        pr.init_window(100, 100, self.title)
        pr.set_target_fps(self.fps)
        self.running: bool = True
        self.worlds: List[World] = []
        self.active_world: int = -1

    def __del__(self):
        pr.close_window()

    def init_camera(self, camera: pr.Camera2D):
        self.camera = camera

    def update_camera(self, camera: pr.Camera2D):
        self.camera = camera

    def add_world(self, world: World):
        self.worlds.append(world)

    def set_active_world(self, World: int):
        if (len(self.worlds) - 1) < World:
            return False

        if self.active_world != -1:
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
        pr.begin_mode_2d(self.camera)
        self.worlds[self.active_world].render()
        pr.end_mode_2d()
        pr.end_drawing()

    def run(self):
        if self.active_world == -1:
            raise ValueError("No active world set")
        while self.running:
            self.update()
            self.render()


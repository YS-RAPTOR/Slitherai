import pyray as pr

from Slitherai.Environment.CameraComponent import ServerCameraComponent
from Slitherai.Environment.Constants import IS_DEBUG, OPTIMAL_RESOLUTION_WIDTH
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Food import FoodSpawner
from Slitherai.Environment.NetworkManagerComponent import ServerNetworkManager
from Slitherai.AI.AiManager import AiManager

from typing import List
from time import time
from Slitherai.Environment.Core.World import World


class Server(Application):
    def __init__(
        self,
        title: str,
        fps: int,
        gui: bool = True,
        host: str = "0.0.0.0",
        port: int = 8888,
    ):
        self.gui: bool = gui
        if gui:
            self.host: str = host
            self.port: int = port
            super().__init__(title, fps)
            self.aspect_ratio: float = 9 / 16

            self.width: int = int(pr.get_monitor_width(0) / 2)
            self.height: int = int(self.width * self.aspect_ratio)

            pr.set_window_size(self.width, self.height)
        else:
            self.host: str = host
            self.port: int = port
            self.running: bool = True
            self.worlds: List[World] = []
            self.active_world: int = -1
            self.frame_time: float = 1 / fps

    def __del__(self):
        if self.gui:
            super().__del__()
        else:
            self.worlds[self.active_world].destroy()

    def no_gui_update(self):
        start_time = time()

        self.worlds[self.active_world].update(self.frame_time)
        if self.active_world != self.next_world:
            self.activate_world()

        self.frame_time = time() - start_time

    def run(self):
        if self.gui:
            super().run()
        else:
            while self.running:
                self.no_gui_update()


if __name__ == "__main__":
    # Initialize the client
    GUI = True
    WORLD_SIZE = 50000
    NUM_AGENTS = 10
    FOOD_TO_SPAWN = 5000
    HAS_AI = False
    server = Server("Slitherai", 60, GUI)

    if GUI:
        center = pr.Vector2(server.width / 2, server.height / 2)
        camera = pr.Camera2D(center, pr.Vector2(WORLD_SIZE // 2, WORLD_SIZE // 2), 0, 1)
        server.init_camera(camera)

    # Initialize the world
    food_spawner = FoodSpawner(server, FOOD_TO_SPAWN)
    components = [ServerNetworkManager(server.host, server.port, server), food_spawner]
    if GUI:
        components.append(ServerCameraComponent(server))

    if HAS_AI:
        components.append(
            AiManager(server, "./Finished Models/134AM", food_spawner, NUM_AGENTS)
        )

    manager = Entity(
        "Manager",
        components,
    )

    world = GridWorld(WORLD_SIZE, 50)
    world.add_entity(manager)
    server.add_world(world)
    server.set_active_world(0)
    server.activate_world()

    # Start the client
    print("Starting server...")
    print(f"Listening on {server.host}:{server.port}")
    server.run()
    print("Server closed.")


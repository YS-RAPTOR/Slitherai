import pyray as pr
import time

from Slitherai.Environment.CameraComponent import ServerCameraComponent
from Slitherai.Environment.Constants import IS_DEBUG, OPTIMAL_RESOLUTION_WIDTH
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Food import FoodSpawner
from Slitherai.Environment.NetworkManagerComponent import ServerNetworkManager

from typing import List
from Slitherai.Environment.Core.World import World


class Server(Application):
    def __init__(
        self,
        title: str,
        fps: int,
        host: str = "localhost",
        port: int = 2003,
    ):
        self.host: str = host
        self.port: int = port
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = int(pr.get_monitor_width(0) / 4)
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)


if __name__ == "__main__":
    # Initialize the client
    server = Server("Slitherai", 60)
    center = pr.Vector2(server.width / 2, server.height / 2)
    camera = pr.Camera2D(center, pr.Vector2(25000, 25000), 0, 1)
    server.init_camera(camera)

    # Initialize the world
    manager = Entity(
        "Manager",
        [
            ServerCameraComponent(server),
            ServerNetworkManager(server.host, server.port, server),
            FoodSpawner(server),
        ],
    )

    world = GridWorld(50000, 50)
    world.add_entity(manager)
    server.add_world(world)
    server.set_active_world(0)
    server.activate_world()

    # Start the client
    server.run()


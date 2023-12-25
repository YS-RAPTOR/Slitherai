import pyray as pr

from Slitherai.Environment.CameraComponent import ServerCameraComponent
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Food import FoodSpawner
from Slitherai.Environment.NetworkManagerComponent import ServerNetworkManager


class Server(Application):
    def __init__(self, title: str, fps: int, host: str = "localhost", port: int = 2003):
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = pr.get_monitor_width(0)
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)
        # pr.toggle_fullscreen()

    def update(self):
        super().update()


if __name__ == "__main__":
    # Initialize the client
    server = Server("Slitherai", 60)
    center = pr.Vector2(server.width / 2, server.height / 2)
    zoom = pr.get_screen_width() / OPTIMAL_RESOLUTION_WIDTH
    camera = pr.Camera2D(center, pr.Vector2(25000, 25000), 0, zoom)
    server.init_camera(camera)

    pr.set_window_size(server.width, server.height)

    # Initialize the world
    manager = Entity(
        "Manager",
        [
            ServerCameraComponent(server),
            ServerNetworkManager("127.0.0.1", 2003, server),
            FoodSpawner(server),
        ],
    )
    # TODO: Fix Changing directions for snake

    world = GridWorld(50000, 50)
    world.add_entity(manager)
    server.add_world(world)
    server.set_active_world(0)

    # Start the client
    server.run()


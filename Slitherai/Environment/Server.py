from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.CameraComponent import ServerCameraComponent
from Slitherai.Environment.NetworkManagerComponent import ServerNetworkManager
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
import pyray as pr


class Server(Application):
    def __init__(self, title: str, fps: int, host: str = "localhost", port: int = 2003):
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = OPTIMAL_RESOLUTION_WIDTH
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)
        pr.toggle_fullscreen()

    def update(self):
        super().update()


if __name__ == "__main__":
    # Initialize the client
    server = Server("Slitherai", 60)
    center = pr.Vector2(server.width / 2, server.height / 2)
    camera = pr.Camera2D(center, pr.Vector2(0, 0), 0, 1)
    server.init_camera(camera)

    # Initialize the world
    cameraController = Entity(
        "Manager",
        [
            ServerCameraComponent(server),
            ServerNetworkManager("127.0.0.1", 2003, server),
        ],
    )

    world = World()
    world.add_entity(cameraController)
    server.add_world(world)
    server.set_active_world(0)

    # Start the client
    server.run()


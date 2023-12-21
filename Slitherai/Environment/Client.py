from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.NetworkManagerComponent import ClientNetworkManager
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
import pyray as pr


class Client(Application):
    def __init__(self, title: str, fps: int):
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = OPTIMAL_RESOLUTION_WIDTH
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)
        print(f"Window size: {self.width}x{self.height}")


if __name__ == "__main__":
    # Initialize the client
    client = Client("Slitherai", 60)
    center = pr.Vector2(client.width / 2, client.height / 2)
    camera = pr.Camera2D(center, pr.Vector2(0, 0), 0, 1)
    client.init_camera(camera)

    # Initialize the world
    center = pr.Vector2(client.width / 2, client.height / 2)
    snake = Entity("Manager", [ClientNetworkManager(("127.0.0.1", 2003), client)])

    world = World()
    world.add_entity(snake)
    client.add_world(world)
    client.set_active_world(0)

    # Start the client
    client.run()


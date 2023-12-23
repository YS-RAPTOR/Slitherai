from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.NetworkManagerComponent import ClientNetworkManager
from Slitherai.Environment.ButtonComponent import StartButton
from Slitherai.Environment.Instructions import Instructions
from Slitherai.Environment.TextField import TextField
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
import pyray as pr
import radyx


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
    zoom = pr.get_screen_width() / OPTIMAL_RESOLUTION_WIDTH
    camera = pr.Camera2D(center, pr.Vector2(0, 0), 0, zoom)
    client.init_camera(camera)
    center = pr.Vector2(client.width / 2, client.height / 2)

    button_width = 200
    button_height = 50
    button_x = center.x - button_width / 2
    button_y = center.y - button_height / 2 + 40

    area_width = 300
    area_height = 30
    area_x = center.x - area_width / 2
    area_y = center.y - area_height / 2 - 40

    network_manager = ClientNetworkManager(("", 0), client)

    # Initialize title screen world
    ui = Entity(
        "UI",
        [
            Instructions(10, 10, 20, pr.Color(128, 128, 128, 255), camera),
            TextField(
                "Server Address",
                20,
                pr.Rectangle(area_x, area_y, area_width, area_height),
                20,
                pr.Color(128, 128, 128, 255),
                pr.Color(0, 0, 0, 255),
                camera,
            ),
            StartButton(
                pr.Rectangle(button_x, button_y, button_width, button_height),
                camera,
                client,
                1,
                network_manager,
            ),
        ],
    )

    title_screen = World()
    title_screen.add_entity(ui)
    client.add_world(title_screen)

    # Initialize the game world
    manager = Entity("Manager", [network_manager])
    world = World()
    world.add_entity(manager)
    client.add_world(world)

    client.set_active_world(0)

    # Start the client
    client.run()


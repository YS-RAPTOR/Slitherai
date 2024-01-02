import pyray as pr

from Slitherai.Environment.ButtonComponent import (
    ChangeWorldButton,
    PauseButton,
    QuitButton,
    StartButton,
)
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Instructions import Instructions
from Slitherai.Environment.NetworkManagerComponent import ClientNetworkManager
from Slitherai.Environment.TextField import TextField


class Client(Application):
    def __init__(self, title: str, fps: int):
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = OPTIMAL_RESOLUTION_WIDTH
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)
        pr.set_exit_key(pr.KeyboardKey.KEY_RIGHT_ALT)


if __name__ == "__main__":
    # Initialize the client
    client = Client("Slitherai", 60)
    center = pr.Vector2(client.width / 2, client.height / 2)
    zoom = pr.get_screen_width() / OPTIMAL_RESOLUTION_WIDTH
    camera = pr.Camera2D(center, pr.Vector2(0, 0), 0, zoom)
    client.init_camera(camera)
    center = pr.Vector2(client.width / 2, client.height / 2)

    button_width = 250
    button_height = 50
    button_x = center.x - button_width / 2
    button_y = center.y - button_height / 2 + 40

    area_width = 300
    area_height = 30
    area_x = center.x - area_width / 2
    area_y = center.y - area_height / 2 - 40

    network_manager = ClientNetworkManager(("", 0), client)

    # Initialize title screen world
    titleUi = Entity(
        "TitleUI",
        [
            Instructions(10, 10, 20, pr.Color(128, 128, 128, 255), camera),
            TextField(
                "Server Address",
                20,
                pr.Rectangle(area_x, area_y, area_width, area_height),
                20,
                pr.Color(128, 128, 128, 255),
                pr.Color(0, 0, 0, 255),
            ),
            StartButton(
                pr.Rectangle(button_x, button_y, button_width, button_height),
                client,
                1,
                network_manager,
            ),
            QuitButton(
                pr.Rectangle(button_x, button_y + 60, button_width, button_height),
                client,
            ),
        ],
    )

    title_screen = World()
    title_screen.add_ui_entity(titleUi)
    client.add_world(title_screen)

    # Pause UI
    pauseUI = Entity(
        "PauseUI",
        [
            Instructions(3, 130, 20, pr.Color(128, 128, 128, 255), camera),
            ChangeWorldButton(
                "Back To Menu",
                pr.Rectangle(button_x, button_y, button_width, button_height),
                pr.Color(128, 128, 128, 255),
                client,
                0,
            ),
            QuitButton(
                pr.Rectangle(button_x, button_y + 60, button_width, button_height),
                client,
            ),
        ],
    )

    pause_button = Entity(
        "PauseButton",
        [
            PauseButton(
                pr.Rectangle(button_x, button_y - 60, button_width, button_height),
                pauseUI,
            ),
        ],
    )

    # Initialize the game world
    manager = Entity("Manager", [network_manager])

    world = World()
    world.add_entity(manager)
    world.add_ui_entity(pauseUI)
    world.add_ui_entity(pause_button)
    client.add_world(world)

    respawnUI = Entity(
        "RespawnUI",
        [
            Instructions(10, 10, 20, pr.Color(128, 128, 128, 255), camera),
            ChangeWorldButton(
                "Respawn",
                pr.Rectangle(button_x, button_y - 60, button_width, button_height),
                pr.Color(0, 117, 44, 255),
                client,
                1,
            ),
            ChangeWorldButton(
                "Back To Menu",
                pr.Rectangle(button_x, button_y, button_width, button_height),
                pr.Color(128, 128, 128, 255),
                client,
                0,
            ),
            QuitButton(
                pr.Rectangle(button_x, button_y + 60, button_width, button_height),
                client,
            ),
        ],
    )
    respawn_world = World()
    respawn_world.add_ui_entity(respawnUI)
    client.add_world(respawn_world)

    client.set_active_world(0)
    client.activate_world()

    # Start the client
    client.run()


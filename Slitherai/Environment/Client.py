from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.SnakeBodyComponent import SnakeBodyComponent
import pyray as pr


class Client(Application):
    def __init__(self, title: str, fps: int):
        super().__init__(title, fps)
        self.aspect_ratio: float = 9 / 16

        self.width: int = pr.get_screen_width()
        self.height: int = int(self.width * self.aspect_ratio)

        pr.set_window_size(self.width, self.height)
        pr.toggle_fullscreen()
        print(f"Window size: {self.width}x{self.height}")


if __name__ == "__main__":
    # Initialize the client
    client = Client("Slitherai", 60)

    # Initialize the world
    center = pr.Vector2(client.width / 2, client.height / 2)
    snake = Entity(
        "Current_Player", [SnakeBodyComponent(10, center, pr.Vector2(0, -1))]
    )

    world = World()
    world.add_entity(snake)
    client.add_world(world)
    client.set_active_world(0)

    # Start the client
    client.run()


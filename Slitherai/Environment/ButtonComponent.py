from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.TextField import TextField
from Slitherai.Environment.NetworkManagerComponent import ClientNetworkManager
import pyray as pr


class ButtonComponent(Component):
    def __init__(
        self,
        text: str,
        font_size: int,
        text_color: pr.Color,
        button_size: pr.Rectangle,
        button_color: pr.Color,
        roundness: float,
        camera: pr.Camera2D,
    ) -> None:
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.button_size = button_size
        self.button_color = button_color
        self.roundness = roundness

        text_width = pr.measure_text(text, self.font_size)
        if text_width > self.button_size.width:
            raise ValueError("Text is too long for button")
        if self.font_size > self.button_size.height:
            raise ValueError("Font size is too large for button")

        position = pr.Vector2(
            (self.button_size.width - text_width) / 2 + self.button_size.x,
            (self.button_size.height - self.font_size) / 2 + self.button_size.y,
        )

        button_pos = pr.Vector2(self.button_size.x, self.button_size.y)

        # convert to screen coordinates to world coordinates
        world_pos = pr.get_screen_to_world_2d(position, camera)
        world_button_pos = pr.get_screen_to_world_2d(button_pos, camera)

        self.x = int(world_pos.x)
        self.y = int(world_pos.y)
        self.button_size.x = world_button_pos.x
        self.button_size.y = world_button_pos.y
        self.camera = camera

    def is_mouse_over(self) -> bool:
        mouse_pos = pr.get_mouse_position()
        mouse_pos = pr.get_screen_to_world_2d(mouse_pos, self.camera)
        return pr.check_collision_point_rec(mouse_pos, self.button_size)

    def update(self, delta_time: float):
        if (
            pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)
            and self.is_mouse_over()
        ):
            self.on_click()

    def render(self):
        pr.draw_rectangle_rounded(
            self.button_size, self.roundness, 0, self.button_color
        )
        pr.draw_text(self.text, self.x, self.y, self.font_size, self.text_color)

    def on_click(self):
        pass


class StartButton(ButtonComponent):
    def __init__(
        self,
        button: pr.Rectangle,
        camera: pr.Camera2D,
        app: Application,
        nextWorld: int,
        client: ClientNetworkManager,
    ):
        super().__init__(
            "Start Game",
            32,
            pr.Color(245, 245, 245, 255),
            button,
            pr.Color(0, 117, 44, 255),
            0.5,
            camera,
        )
        self.app = app
        self.nextWorld = nextWorld
        self.client = client

        # Error handling
        self.error = False
        self.error_size = 20
        self.errorText = "Could not connect to the server"
        self.error_width = pr.measure_text(self.errorText, self.error_size)

        x = 10
        y = self.app.height - 10 - self.error_size
        position = pr.Vector2(x, y)
        world_pos = pr.get_screen_to_world_2d(position, self.camera)
        self.error_x = int(world_pos.x)
        self.error_y = int(world_pos.y)

        self.errorColor = pr.Color(255, 0, 0, 255)
        self.errorTime = 5
        self.time = 0

    def init(self):
        self.textField = self.get_component(TextField.component_id)

    def update(self, delta_time: float):
        super().update(delta_time)
        if self.error:
            self.time -= delta_time
        if self.time <= 0:
            self.error = False

    def render(self):
        super().render()
        if self.error:
            pr.draw_text(
                self.errorText,
                self.error_x,
                self.error_y,
                self.error_size,
                self.errorColor,
            )

    def on_click(self):
        currentWorld = self.app.active_world
        try:
            address, port = self.textField.text.split(":")
            self.client.server_address = (address, int(port))
            self.app.set_active_world(self.nextWorld)
        except:
            self.app.set_active_world(currentWorld)
            self.error = True
            self.time = self.errorTime


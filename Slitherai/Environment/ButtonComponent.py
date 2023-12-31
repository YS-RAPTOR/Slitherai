import pyray as pr

from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.NetworkManagerComponent import ClientNetworkManager
from Slitherai.Environment.TextField import TextField


class ButtonComponent(Component):
    def __init__(
        self,
        text: str,
        font_size: int,
        text_color: pr.Color,
        button_size: pr.Rectangle,
        button_color: pr.Color,
        roundness: float,
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

        self.position = pr.Vector2(
            (self.button_size.width - text_width) / 2 + self.button_size.x,
            (self.button_size.height - self.font_size) / 2 + self.button_size.y,
        )

        self.button_pos = pr.Vector2(self.button_size.x, self.button_size.y)

    def is_mouse_over(self) -> bool:
        return pr.check_collision_point_rec(pr.get_mouse_position(), self.button_size)

    def update(self, delta_time: float):
        if (
            pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)
            and self.is_mouse_over()
        ):
            self.on_click()

    def draw(self, camera: pr.Camera2D):
        pr.draw_rectangle_rounded(
            self.button_size, self.roundness, 0, self.button_color
        )
        pr.draw_text_ex(
            pr.get_font_default(),
            self.text,
            self.position,
            self.font_size,
            1,
            self.text_color,
        )

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True

    def on_click(self):
        pass


class StartButton(ButtonComponent):
    def __init__(
        self,
        button: pr.Rectangle,
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
        )
        self.app = app
        self.nextWorld = nextWorld
        self.client = client

        # Error handling
        self.error = False
        self.error_size = 20
        self.errorText = "Could not connect to the server"
        self.error_width = pr.measure_text(self.errorText, self.error_size)

        self.error_x = 10
        self.error_y = self.app.height - 10 - self.error_size

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

    def draw(self, camera: pr.Camera2D):
        super().draw(camera)
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
            self.app.activate_world()
        except Exception:
            self.app.set_active_world(currentWorld)
            self.error = True
            self.time = self.errorTime


class QuitButton(ButtonComponent):
    def __init__(
        self,
        button: pr.Rectangle,
        app: Application,
    ):
        super().__init__(
            "Quit Game",
            32,
            pr.Color(245, 245, 245, 255),
            button,
            pr.Color(230, 41, 55, 255),
            0.5,
        )
        self.app = app

    def draw(self, camera: pr.Camera2D):
        super().draw(camera)

    def on_click(self):
        self.app.quit()


class ChangeWorldButton(ButtonComponent):
    def __init__(
        self,
        text: str,
        button: pr.Rectangle,
        button_color: pr.Color,
        app: Application,
        nextWorld: int,
    ):
        super().__init__(
            text,
            32,
            pr.Color(245, 245, 245, 255),
            button,
            button_color,
            0.5,
        )
        self.app = app
        self.nextWorld = nextWorld

    def draw(self, camera: pr.Camera2D):
        super().draw(camera)

    def on_click(self):
        self.app.set_active_world(self.nextWorld)


class PauseButton(ButtonComponent):
    def __init__(self, button: pr.Rectangle, pause_entity: Entity):
        super().__init__(
            "Resume",
            32,
            pr.Color(245, 245, 245, 255),
            button,
            pr.Color(0, 117, 44, 255),
            0.5,
        )
        self.pause_entity = pause_entity

    def init(self):
        self.entity = self.get_entity()
        self.entity.can_draw = False
        self.pause_entity.is_active = False

    def pause(self):
        self.entity.can_draw = True
        self.pause_entity.is_active = True

    def resume(self):
        self.entity.can_draw = False
        self.pause_entity.is_active = False

    def draw(self, camera: pr.Camera2D):
        super().draw(camera)

    def update(self, delta_time: float):
        super().update(delta_time)
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            if self.entity.can_draw:
                self.resume()
            else:
                self.pause()

    def on_click(self):
        self.resume()

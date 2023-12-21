from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Application import Application
import pyray as pr


class ServerCameraComponent(Component):
    def __init__(self, app: Application) -> None:
        super().__init__()
        self.app = app
        self.speed = 100

    def get_input_direction(self):
        x = 0
        y = 0

        if pr.is_key_down(pr.KeyboardKey.KEY_W):
            y = -1
        elif pr.is_key_down(pr.KeyboardKey.KEY_S):
            y = 1

        if pr.is_key_down(pr.KeyboardKey.KEY_D):
            x = 1
        elif pr.is_key_down(pr.KeyboardKey.KEY_A):
            x = -1

        self.input_dir = pr.vector2_normalize(
            pr.Vector2(x * self.speed, y * self.speed)
        )

    def update(self, delta_time: float):
        self.get_input_direction()
        updated_target = pr.vector2_add(self.app.camera.target, self.input_dir)
        update_camera = pr.Camera2D(
            self.app.camera.offset,
            updated_target,
            self.app.camera.rotation,
            self.app.camera.zoom,
        )
        self.app.update_camera(update_camera)


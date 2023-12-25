import pyray as pr

from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Component import Component


class ServerCameraComponent(Component):
    def __init__(self, app: Application) -> None:
        super().__init__()
        self.app = app
        self.speed = 1000
        self.camera = True
        self.camera_location_pos = pr.Vector2(10, 40)
        self.color = pr.Color(128, 128, 128, 255)

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

        self.input_dir = pr.vector2_normalize(pr.Vector2(x, y))

    def update(self, delta_time: float):
        self.get_input_direction()

        updated_target = pr.vector2_add(
            self.app.camera.target,
            pr.vector2_scale(self.input_dir, self.speed * delta_time),
        )
        update_camera = pr.Camera2D(
            self.app.camera.offset,
            updated_target,
            self.app.camera.rotation,
            self.app.camera.zoom,
        )
        self.app.update_camera(update_camera)

    def render(self, camera: pr.Camera2D):
        pos = pr.get_screen_to_world_2d(self.camera_location_pos, camera)
        pr.draw_text(
            f"Camera: {int(camera.target.x)},{int(camera.target.y)}",
            int(pos.x),
            int(pos.y),
            20,
            self.color,
        )


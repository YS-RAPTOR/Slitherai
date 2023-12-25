import pyray as pr

from Slitherai.Environment.Constants import INSTRUCTIONS
from Slitherai.Environment.Core.Component import Component


class Instructions(Component):
    def __init__(
        self, x: int, y: int, font_size: int, font_color: pr.Color, camera: pr.Camera2D
    ):
        position = pr.Vector2(x, y)
        world_pos = pr.get_screen_to_world_2d(position, camera)
        self.x = int(world_pos.x)
        self.y = int(world_pos.y)
        self.font_size = font_size
        self.font_color = font_color

    def render(self, camera: pr.Camera2D):
        pr.draw_text(INSTRUCTIONS, self.x, self.y, self.font_size, self.font_color)

    def can_render(self, camera: pr.Camera2D) -> bool:
        return True

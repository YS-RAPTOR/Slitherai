import pyray as pr

from Slitherai.Environment.Constants import INSTRUCTIONS
from Slitherai.Environment.Core.Component import Component


class Instructions(Component):
    def __init__(
        self, x: int, y: int, font_size: int, font_color: pr.Color, camera: pr.Camera2D
    ):
        self.pos = pr.Vector2(x, y)
        self.font_size = font_size
        self.font_color = font_color

    def draw(self, camera: pr.Camera2D):
        pr.draw_text_ex(
            pr.get_font_default(),
            INSTRUCTIONS,
            self.pos,
            self.font_size,
            1,
            self.font_color,
        )

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True


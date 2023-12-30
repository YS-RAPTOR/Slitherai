import pyray as pr

from Slitherai.Environment.Core.Component import Component


class TextField(Component):
    def __init__(
        self,
        label,
        label_font_size: int,
        text_region: pr.Rectangle,
        text_font_size: int,
        idle_color: pr.Color,
        color: pr.Color,
    ) -> None:
        self.label = label
        self.label_font_size = label_font_size
        self.text_region = text_region
        self.text_font_size = text_font_size

        self.text: str = ""
        self.is_active = False

        self.label_x = int(self.text_region.x + 5)
        self.label_y = int(self.text_region.y - 5 - self.label_font_size)

        self.idle_color = idle_color
        self.color = color

        self.roundness = 0.1
        self.border_width = 2

        self.center_text()

    def center_text(self):
        self.text_width = pr.measure_text(self.text, self.text_font_size)
        self.text_x = int(
            (self.text_region.width - self.text_width) / 2 + self.text_region.x
        )
        self.text_y = int(
            (self.text_region.height - self.text_font_size) / 2 + self.text_region.y
        )

    def is_mouse_over(self) -> bool:
        return pr.check_collision_point_rec(pr.get_mouse_position(), self.text_region)

    def update(self, delta_time: float):
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            if self.is_mouse_over():
                self.is_active = True
            else:
                self.is_active = False

        if self.is_active:
            if pr.is_key_pressed(pr.KeyboardKey.KEY_BACKSPACE):
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self.center_text()
            else:
                while self.text_width < self.text_region.width - 15:
                    key = pr.get_char_pressed()
                    if key == 0:
                        break
                    key = chr(key)
                    if key.isprintable():
                        self.text += key
                self.center_text()

    def draw(self, camera: pr.Camera2D):
        if self.is_active:
            pr.draw_rectangle_rounded_lines(
                self.text_region,
                self.roundness,
                0,
                self.border_width,
                self.color,
            )
        else:
            pr.draw_rectangle_rounded_lines(
                self.text_region,
                self.roundness,
                0,
                self.border_width,
                self.idle_color,
            )

        # Draw label
        pr.draw_text(
            self.label, self.label_x, self.label_y, self.label_font_size, self.color
        )

        # Draw text
        pr.draw_text(
            self.text, self.text_x, self.text_y, self.text_font_size, self.color
        )

    def can_draw(self, camera: pr.Camera2D) -> bool:
        return True


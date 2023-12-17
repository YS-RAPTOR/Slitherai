class Renderer:
    def __init__(self) -> None:
        self.render_queue = []

    def add_to_render_queue(self, renderable: Renderable) -> None:
        self.render_queue.append(renderable)

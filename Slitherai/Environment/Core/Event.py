class Event:
    def __init__(self, type: int, **kwargs):
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)


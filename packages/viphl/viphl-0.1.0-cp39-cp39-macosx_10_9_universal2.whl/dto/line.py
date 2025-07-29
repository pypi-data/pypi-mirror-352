from dataclasses import dataclass


@dataclass
class Line:
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0

    def reset(self):
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0


#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from typing import Tuple

from PySide6.QtGui import QColor


def color_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> QColor:
    return QColor(rgb[0], rgb[1], rgb[2], a)


def rgba_tuple_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> Tuple[float, float, float, float]:
    return rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, a / 255.0


class Colors:
    def __init__(self):
        self.colors = [
            (100, 100, 255),
            (255, 100, 100),
            (100, 200, 100),
            (255, 100, 0),
            (200, 100, 200),
            (100, 200, 200),
            (100, 100, 100),
        ]
        self.index = 0

    def get_color_list(self):
        color = self.colors[self.index]
        self.index += 1
        if self.index >= len(self.colors):
            self.index = 0
        return color

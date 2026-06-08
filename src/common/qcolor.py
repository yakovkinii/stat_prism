#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Tuple

from PySide6.QtGui import QColor

from src.common.theme import THEME


def color_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> QColor:
    return QColor(rgb[0], rgb[1], rgb[2], a)


def rgba_tuple_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> Tuple[float, float, float, float]:
    return rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, a / 255.0


class Colors:
    def __init__(self):
        # Palette comes from the active theme so series colours follow the theme.
        self.colors = list(THEME.current.palette)
        self.index = 0

    def get_color_list(self):
        color = self.colors[self.index]
        self.index += 1
        if self.index >= len(self.colors):
            self.index = 0
        return color

#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from typing import Tuple

from PySide6.QtGui import QColor

from src.common.theme import THEME


def color_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> QColor:
    return QColor(rgb[0], rgb[1], rgb[2], a)


def rgba_tuple_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> Tuple[float, float, float, float]:
    return rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, a / 255.0


class Colors:
    def __init__(self):
        # Palette comes from the active theme so series colors follow the theme.
        self.colors = list(THEME.current.palette)
        self.index = 0

    def get_color_list(self):
        color = self.colors[self.index]
        self.index += 1
        if self.index >= len(self.colors):
            self.index = 0
        return color

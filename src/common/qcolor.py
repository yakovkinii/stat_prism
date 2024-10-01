from typing import Tuple

from PySide6.QtGui import QColor


def color_from_rgb_and_a(rgb: Tuple[int, int, int], a: int) -> QColor:
    return QColor(rgb[0], rgb[1], rgb[2], a)

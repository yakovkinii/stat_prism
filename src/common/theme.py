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


from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from src.common.config import read_plot_theme


class Themes(Enum):
    DEFAULT = "Default"
    STRICT = "Strict"
    DARK = "Dark"


# A theme supplies only defaults; a user's per-plot tweak is preserved across recomputes (see
# PlotV2.load_settings_from). Sizes/fonts are identical across themes but kept here so every
# default sits together.
@dataclass(frozen=True)
class PlotTheme:
    # Series color cycle (also feeds the color-picker "base" row).
    palette: List[Tuple[int, int, int]]
    # Figure chrome.
    frame_color: Tuple[int, int, int]
    background_color: Tuple[int, int, int]
    # Text color for tick labels, axis titles and the legend. Defaults to black; the Dark
    # theme overrides it to near-white so text is readable on the dark figure background.
    text_color: Tuple[int, int, int]
    # Per-series appearance.
    line_alpha: int
    line_width: int
    line_style: str
    bar_fill_alpha: int
    box_fill_alpha: int
    scatter_fill_alpha: int
    scatter_line_alpha: int
    point_size: int
    marker_shape: str
    band_fill_alpha: int
    # Axis-title layout preset (theme-controlled, like colors).
    axis_layout: str = "Centered"
    # Background opacity (0-255) and frame/grid options (theme-controlled).
    background_alpha: int = 255
    box_frame: bool = True  # show top+right spines (full box) vs only left+bottom
    gridlines: str = "None"  # None / Both / Horizontal / Vertical
    # Sizes / fonts -- shared (identical) across themes, kept here so every default
    # is collected in one place.
    plot_size: int = 600  # width in px
    plot_aspect: float = 0.8  # height / width
    axis_title_font_size: int = 18
    tick_label_font_size: int = 14
    legend_font_size: int = 12
    frame_thickness: float = 1.0
    margin: float = 0.1  # whitespace (inches) around the plot, i.e. savefig pad_inches


# The original StatPrism look: pastel color cycle, gray frame.
_DEFAULT = PlotTheme(
    palette=[
        (100, 100, 255),
        (255, 100, 100),
        (100, 200, 100),
        (255, 100, 0),
        (200, 100, 200),
        (100, 200, 200),
        (100, 100, 100),
    ],
    frame_color=(128, 128, 128),
    background_color=(255, 255, 255),
    text_color=(0, 0, 0),
    line_alpha=200,
    line_width=3,
    line_style="Solid",
    bar_fill_alpha=50,
    box_fill_alpha=50,
    scatter_fill_alpha=100,
    scatter_line_alpha=0,
    point_size=8,
    marker_shape="Circle",
    band_fill_alpha=50,
    axis_layout="Centered",
    background_alpha=255,  # opaque white figure background
)

# A stricter, print-friendly look: a saturated "standard" color progression
# (black, red, blue, dark green, ...), black frame, more solid fills. The picker
# derives lighter/darker shades and a grayscale (neutrals) row from these, so the
# base row stays the full-strength colors (#000, #F00, #00F, ...).
_STRICT = PlotTheme(
    palette=[
        (0, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 100, 0),
        (128, 0, 128),
        (255, 140, 0),
        (0, 128, 128),
    ],
    frame_color=(0, 0, 0),
    background_color=(255, 255, 255),
    text_color=(0, 0, 0),
    line_alpha=250,
    line_width=2,
    line_style="Solid",
    bar_fill_alpha=200,
    box_fill_alpha=100,
    scatter_fill_alpha=200,
    scatter_line_alpha=250,
    point_size=8,
    marker_shape="Circle",
    band_fill_alpha=100,
    axis_layout="Centered",
    box_frame=False,
    background_alpha=255,
)

# Dark look: dark background, light frame/text, brighter series colors.
_DARK = PlotTheme(
    palette=[
        (120, 160, 255),
        (255, 120, 120),
        (120, 220, 120),
        (255, 180, 80),
        (220, 140, 220),
        (120, 220, 220),
        (210, 210, 210),
    ],
    frame_color=(180, 180, 180),
    background_color=(38, 38, 38),
    text_color=(235, 235, 235),
    line_alpha=250,
    line_width=3,
    line_style="Solid",
    bar_fill_alpha=130,
    box_fill_alpha=130,
    scatter_fill_alpha=160,
    scatter_line_alpha=0,
    point_size=8,
    marker_shape="Circle",
    band_fill_alpha=110,
    axis_layout="Centered",
)

_THEMES: Dict[Themes, PlotTheme] = {
    Themes.DEFAULT: _DEFAULT,
    Themes.STRICT: _STRICT,
    Themes.DARK: _DARK,
}


class ThemeManager:
    def __init__(self, theme: Themes = Themes.DEFAULT):
        self._theme = theme

    @property
    def current(self) -> PlotTheme:
        return _THEMES[self._theme]

    def name(self) -> str:
        # Used to detect theme switches (compared against a plot's stored theme name).
        return self._theme.value

    def set_theme(self, theme: Themes):
        self._theme = theme


def _initial_plot_theme() -> Themes:
    try:  # an unrecognized saved plot theme falls back to Default
        return Themes(read_plot_theme())
    except ValueError:
        return Themes.DEFAULT


THEME = ThemeManager(_initial_plot_theme())

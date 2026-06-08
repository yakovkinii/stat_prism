#  Copyright (c) 2023 StatPrism Team. All rights reserved.

"""Central place for plot *default* appearance ("themes").

Every default that the per-plot settings controls can later override lives here, so
the look of all plots can be switched in one place. Themes differ in colours /
grayscale; sizes and fonts are intentionally kept identical across themes (but still
listed here so all defaults sit together).

A theme only supplies *defaults*. Once a user tweaks a control on a specific plot,
that tweak is preserved across recomputes (see PlotV2.load_settings_from); switching
theme re-applies the new colour defaults to plots while keeping user content (titles)
and any size tweaks.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class Themes(Enum):
    DEFAULT = "Default"
    STRICT = "Strict"


@dataclass(frozen=True)
class PlotTheme:
    # Series colour cycle (also feeds the colour-picker "base" row).
    palette: List[Tuple[int, int, int]]
    # Figure chrome.
    frame_color: Tuple[int, int, int]
    background_color: Tuple[int, int, int]
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
    # Sizes / fonts -- shared (identical) across themes, kept here so every default
    # is collected in one place.
    plot_x_size: int = 600
    plot_y_size: int = 500
    axis_title_font_size: int = 18
    tick_label_font_size: int = 14
    legend_font_size: int = 12
    frame_thickness: float = 1.0


# The original StatPrism look: pastel colour cycle, grey frame.
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
)

# A stricter, print-friendly look: a saturated "standard" colour progression
# (black, red, blue, dark green, ...), black frame, more solid fills. The picker
# derives lighter/darker shades and a grayscale (neutrals) row from these, so the
# base row stays the full-strength colours (#000, #F00, #00F, ...).
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
)

_THEMES: Dict[Themes, PlotTheme] = {
    Themes.DEFAULT: _DEFAULT,
    Themes.STRICT: _STRICT,
}


class ThemeManager:
    def __init__(self, theme: Themes = Themes.DEFAULT):
        self._theme = theme

    @property
    def current(self) -> PlotTheme:
        return _THEMES[self._theme]

    def name(self) -> str:
        """Identifier of the active theme (used to detect theme switches)."""
        return self._theme.value

    def set_theme(self, theme: Themes):
        self._theme = theme


THEME = ThemeManager()

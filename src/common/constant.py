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


from enum import Enum

import qtawesome as qta
from PySide6.QtGui import QColor

from src.pyside_ext.styling import Style

MDASH = "—"
NDASH = "–"
TIMES = "×"
WARNING = "⚠"
RARROW = "→"
LRARROW = "↔"
UARROW = "↑"
DARROW = "↓"
CROSS = "✕"
RTRIANGLE = "▸"
RESET_ARROW = "⟲"
ELLIPSIS = "…"
MU = "μ"
SIGMA = "σ"
RHO = "ρ"
MINUS = "−"
PROPORTIONAL = "∝"

TABLE_OR_PLOT_ID_PLACEHOLDER = "<table_or_plot_id>"


class ColumnType(Enum):
    NOMINAL = "Nominal"
    NUMERIC = "Numeric"
    ORDINAL = "Ordinal"
    ID = "ID"


# The mandatory identifier column is always named exactly this.
ID_COLUMN_NAME = "ID"


# Pastel palette for per-column tagging (data-viewer header backgrounds, column-selector
# items). A column's color is None/0 when untagged. Kept deliberately soft so text stays
# readable on top.
PASTEL_PALETTE = [
    "#ffb3b3",  # red
    "#ffcf9e",  # orange
    "#fdf29a",  # yellow
    "#d0ee9c",  # lime
    "#9fe6c4",  # teal
    "#a6d5ff",  # blue
    "#bcb6ff",  # indigo
    "#e0b0ff",  # violet
    "#ffabda",  # pink
    "#dcdcdc",  # gray
]


def hex_to_argb(color):
    """'#rrggbb' (or 'rrggbb') -> openpyxl 'AARRGGBB' (opaque). None for falsy/untagged."""
    if not isinstance(color, str) or not color:
        return None
    return "FF" + color.lstrip("#").upper()


def argb_to_hex(argb):
    """openpyxl fill color ('AARRGGBB' or 'RRGGBB') -> '#rrggbb'. None if not a literal RGB."""
    if not isinstance(argb, str) or len(argb) not in (6, 8):
        return None
    rgb = argb[-6:]
    return "#" + rgb.lower()


# Type colors come from the central scheme (Style.Color); medium-bright so the icons read on
# the dark UI as well as on the (light) pastel column tags in the data viewer.
_TYPE_ICON_GLYPH = {
    ColumnType.NUMERIC: "mdi.numeric",
    ColumnType.NOMINAL: "mdi6.alphabetical-variant",
    ColumnType.ORDINAL: "ph.chart-bar",
    ColumnType.ID: "mdi.key",
}
_TYPE_ICON_COLOR = {
    ColumnType.NUMERIC: Style.Color.TypeNumeric.value,
    ColumnType.NOMINAL: Style.Color.TypeNominal.value,
    ColumnType.ORDINAL: Style.Color.TypeOrdinal.value,
    ColumnType.ID: Style.Color.TypeId.value,
}

# Dark, saturated variants for drawing on a column's (light pastel) color tag, where the
# normal theme-tinted icons -- light in the dark UI theme -- would be hard to see.
_TYPE_ICON_COLOR_ON_LIGHT = {
    ColumnType.NUMERIC: "darkblue",
    ColumnType.NOMINAL: "darkred",
    ColumnType.ORDINAL: "darkgreen",
    ColumnType.ID: "#6a1b9a",
}

# Light, bright variants for drawing on a dark background (a dark color tag, or the dark header
# chrome). Theme-independent so the choice can be made per background luminance, not per UI theme.
_TYPE_ICON_COLOR_ON_DARK = {
    ColumnType.NUMERIC: "#5b9bd5",
    ColumnType.NOMINAL: "#e57373",
    ColumnType.ORDINAL: "#81c784",
    ColumnType.ID: "#b388d9",
}

COLUMN_TYPE_ICONS = {
    ctype: qta.icon(glyph, color=_TYPE_ICON_COLOR[ctype], opacity=0.9) for ctype, glyph in _TYPE_ICON_GLYPH.items()
}

# Use when the icon sits on a light background (a pastel color tag, or a light header).
COLUMN_TYPE_ICONS_ON_LIGHT = {
    ctype: qta.icon(glyph, color=_TYPE_ICON_COLOR_ON_LIGHT[ctype], opacity=0.95)
    for ctype, glyph in _TYPE_ICON_GLYPH.items()
}

# Use when the icon sits on a dark background (a dark color tag, or the dark header chrome).
COLUMN_TYPE_ICONS_ON_DARK = {
    ctype: qta.icon(glyph, color=_TYPE_ICON_COLOR_ON_DARK[ctype], opacity=0.95)
    for ctype, glyph in _TYPE_ICON_GLYPH.items()
}


def is_light_color(color) -> bool:
    """True when a color string is light enough that dark text/icons read better on it than light
    ones (by perceived luminance). Falsy or invalid colors return False."""
    if not (isinstance(color, str) and color):
        return False
    c = QColor(color)
    if not c.isValid():
        return False
    return (0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()) > 140


def column_type_icon(column_type, color):
    """The column-type icon suited to its background: the dark set on a light color tag, the light
    set on a dark tag, and the theme-tinted set when there is no tag (theme-appropriate already)."""
    if isinstance(color, str) and color:
        return (COLUMN_TYPE_ICONS_ON_LIGHT if is_light_color(color) else COLUMN_TYPE_ICONS_ON_DARK)[column_type]
    return COLUMN_TYPE_ICONS[column_type]


def column_text_color(color):
    """Text color for a column name shown on `color`: black on a light tag, white on a dark tag,
    and None (leave the widget/theme default) when there is no tag."""
    if not (isinstance(color, str) and color):
        return None
    return "black" if is_light_color(color) else "white"


BASE_STYLES = (
    f"<style>"
    f".double-spacing {{ line-height: 1.5; }}"
    f".font {{ font-size: {Style.FontSize.regular}; font-family: 'Times New Roman'; }}"
    f"table, th, td {{ border-collapse: collapse; }}"
    f".meta {{ font-size: {Style.FontSize.smaller}; }}"
    f"</style>"
)


class SettingsPanelSize:
    width: int = 320
    popup_minimum_width: int = 700
    tab_width: int = 300
    even_col_width: int = 130
    max_col_width: int = 200

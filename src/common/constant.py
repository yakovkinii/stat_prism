#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from enum import Enum

import qtawesome as qta
from PySide6.QtCore import Qt

DEBUG_LAYOUT = False

COLORS = ["#eee", "#ffcccc", "#ccffcc", "#bbbbff", "#ffffbb", "#ffbbff"]
COLORS_SELECTION = ["#ddd", "#ffbbbb", "#aaffaa", "#aaaaff", "#ffffaa", "#ffaaff"]

MDASH = "—"
NDASH = "–"

TABLE_OR_PLOT_ID_PLACEHOLDER = "<table_or_plot_id>"

PEN_STYLE_MAP = {
    "Solid": Qt.PenStyle.SolidLine,
    "Dash": Qt.PenStyle.DashLine,
    "Dot": Qt.PenStyle.DotLine,
    "Dash-dot": Qt.PenStyle.DashDotLine,
    "None": Qt.PenStyle.NoPen,
}

MARKER_SHAPE_MAP = {
    "Circle": "o",
    "Square": "s",
    "Diamond": "d",
    "Plus": "+",
    "Cross": "x",
    "Star": "star",
}


class ColumnType(Enum):
    NOMINAL = "Nominal"
    NUMERIC = "Numeric"
    ORDINAL = "Ordinal"


COLUMN_TYPE_ICONS = {
    ColumnType.NUMERIC: qta.icon("mdi.numeric", color="darkblue", opacity=0.7),
    ColumnType.NOMINAL: qta.icon("mdi6.alphabetical-variant", color="darkred", opacity=0.7),
    ColumnType.ORDINAL: qta.icon("ph.chart-bar", color="darkgreen", opacity=0.7),
}

BASE_STYLES = (
    "<style>"
    ".double-spacing{"
    "line-height: 2;"
    "}"
    ".font {"
    "font-size: 12pt;"
    "font-family: 'Times New Roman';"
    "}"
    "table, th, td, span {"
    "border-collapse: collapse;"
    "font-size: 12pt;"
    "}"
    "</style>"
)

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
    "Dash-dot-dot": Qt.PenStyle.DashDotDotLine,
    "None": Qt.PenStyle.NoPen,
}

MARKER_SHAPE_MAP = {
    "Circle": "o",
    "Square": "s",
    "Triangle-up": "t",
    "Triangle-down": "d",
    "Diamond": "d",
    "Plus": "+",
    "Cross": "x",
    "Star": "star",
}


class ColumnType(Enum):
    NOMINAL = "Nominal"
    NUMERIC = "Numeric"
    ORDINAL = "Ordinal"
    ORDINAL_UNCONFIRMED = "Ordinal (unconfirmed)"


COLUMN_TYPE_ICONS = {
    ColumnType.NUMERIC: qta.icon("mdi.numeric", color="darkblue", opacity=0.7),
    ColumnType.NOMINAL: qta.icon("mdi6.alphabetical-variant", color="darkred", opacity=0.7),
    ColumnType.ORDINAL: qta.icon("ph.chart-bar", color="darkgreen", opacity=0.7),
    ColumnType.ORDINAL_UNCONFIRMED: qta.icon("ph.chart-bar", color="darkgreen", opacity=0.7),
}

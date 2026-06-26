import math

import numpy as np
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.common.constant import COLUMN_TYPE_ICONS, COLUMN_TYPE_ICONS_ON_LIGHT, ColumnType
from src.data.data import Data
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet

# Custom header-data roles carrying per-column metadata to the painted header.
TYPE_ROLE = QtCore.Qt.UserRole + 101
COLOR_ROLE = QtCore.Qt.UserRole + 102

_STANDARD_MIN_WIDTH = 80
_STANDARD_MAX_WIDTH = 300
_FIXED_WIDTH = 140  # uniform medium width used by the default "Fixed width" mode
_ICON_SIZE = 16

# Column-width modes, in combo order.
_MODE_FIXED = 0
_MODE_STANDARD = 1
_MODE_FIT = 2


def _format_cell(value, sig_figs: int = 5) -> str:
    """Display formatter for the data grid: floats are shown to at most `sig_figs`
    significant figures, but never coarser than the ones place (the integer part is kept
    intact and only the fractional part is rounded). Ints / strings are shown verbatim;
    NaN shows blank."""
    if isinstance(value, (float, np.floating)):
        x = float(value)
        if math.isnan(x):
            return ""
        if math.isinf(x) or x == 0:
            return "0" if x == 0 else str(x)
        magnitude = math.floor(math.log10(abs(x)))
        if abs(x) >= 1:
            decimals = max(0, sig_figs - (magnitude + 1))  # never round the integer part
        else:
            decimals = sig_figs - 1 - magnitude  # keep sig_figs after the leading zeros
        text = f"{round(x, decimals):.{decimals}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    return str(value)


def view_data_popup(parent, data: Data, highlight_rows=None):
    """Show the data in a popup table. `highlight_rows` is an optional set of row positions
    to render in red (used by the Filter module to mark rows it removed)."""
    highlight_rows = set(highlight_rows or [])
    red = QtGui.QBrush(QtGui.QColor(Style.Color.Danger.value))
    n_rows, n_cols = data.n_rows(), data.n_columns()
    model = QtGui.QStandardItemModel(n_rows, n_cols)
    for c in range(n_cols):
        for r in range(n_rows):
            text = _format_cell(data[c][r])
            item = QtGui.QStandardItem(text)
            item.setToolTip(text)  # full value on hover (spec: value tooltips)
            if r in highlight_rows:
                item.setForeground(red)
            model.setItem(r, c, item)
    model.setHorizontalHeaderLabels(data.column_names())

    # Per-column header metadata: full-name tooltip, type (for the icon), colour tag.
    for c in range(n_cols):
        column = data.columns[c]
        model.setHeaderData(c, QtCore.Qt.Horizontal, column.column_name, QtCore.Qt.ToolTipRole)
        model.setHeaderData(c, QtCore.Qt.Horizontal, column.column_type, TYPE_ROLE)
        color = column.color if isinstance(column.color, str) and column.color else ""
        model.setHeaderData(c, QtCore.Qt.Horizontal, color, COLOR_ROLE)

    # The ID column is always the leftmost column (the loader inserts it first); freeze it.
    frozen_column = 0
    for c in range(n_cols):
        if data.columns[c].column_type == ColumnType.ID:
            frozen_column = c
            break

    TablePopup(parent, model, frozen_column)


class CustomHeader(QHeaderView):
    """Header that paints the column-type icon + name on the column's colour tag, optionally
    word-wraps the name, and shows the full name as a tooltip (via the model's ToolTipRole,
    handled by QHeaderView itself)."""

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setSectionsClickable(False)
        self.setHighlightSections(False)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._wrap = False

    def set_wrap(self, wrap: bool):
        self._wrap = wrap
        self.viewport().update()

    def paintSection(self, painter, rect, logicalIndex):
        model = self.model()
        if model is None:
            return
        painter.save()

        color = model.headerData(logicalIndex, self.orientation(), COLOR_ROLE)
        # Tagged columns keep their (light) pastel; untagged headers use the dark chrome.
        background = QtGui.QColor(color) if color else QtGui.QColor(Style.Color.BackgroundElevated.value)
        painter.fillRect(rect, background)

        pen = QtGui.QPen(QtGui.QColor(Style.Color.BorderElevated.value))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        text_rect = rect.adjusted(4, 2, -4, -2)

        column_type = model.headerData(logicalIndex, self.orientation(), TYPE_ROLE)
        # On a (light pastel) colour tag the normal icon is hard to see -> use the darker
        # on-light variant; untagged headers keep the regular theme-tinted icon.
        icon_set = COLUMN_TYPE_ICONS_ON_LIGHT if color else COLUMN_TYPE_ICONS
        icon = icon_set.get(column_type)
        if icon is not None:
            pixmap = icon.pixmap(_ICON_SIZE, _ICON_SIZE)
            icon_y = rect.top() + (rect.height() - _ICON_SIZE) // 2
            painter.drawPixmap(text_rect.left(), icon_y, pixmap)
            text_rect.setLeft(text_rect.left() + _ICON_SIZE + 4)

        text = str(model.headerData(logicalIndex, self.orientation(), QtCore.Qt.DisplayRole))
        if self._wrap:
            flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop | QtCore.Qt.TextWordWrap
        else:
            flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        # Dark text on a light pastel tag; light text on the dark header otherwise.
        text_color = Style.Color.TextOnLight.value if color else Style.Color.Text.value
        painter.setPen(QtGui.QPen(QtGui.QColor(text_color)))
        painter.drawText(text_rect, flags, text)

        painter.restore()


class DataTableView(QTableView):
    """Read-only data grid with a frozen left (ID) column. The frozen column is a second
    table view stacked over the left edge, sharing the model and synced for vertical
    scrolling, column width and row heights."""

    def __init__(self, model, frozen_column: int = 0):
        super().__init__()
        self._frozen_column = frozen_column
        self.setModel(model)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.verticalHeader().hide()
        self.setHorizontalHeader(CustomHeader(QtCore.Qt.Horizontal, self))
        self.horizontalHeader().setHighlightSections(False)
        self.setShowGrid(False)
        self._apply_style(self)

        self.frozen = QTableView(self)
        self._init_frozen(model)

    @staticmethod
    def _apply_style(view):
        set_stylesheet(
            view,
            css("QTableView", font_size="10pt", color=Style.Color.Text, background=Style.Color.Background, border="none", outline="none"),
            css("QTableView::item", border_bottom=f"1px solid {Style.Color.Border}"),
        )

    def _init_frozen(self, model):
        frozen = self.frozen
        frozen.setModel(model)
        frozen.setHorizontalHeader(CustomHeader(QtCore.Qt.Horizontal, frozen))
        frozen.horizontalHeader().setHighlightSections(False)
        frozen.verticalHeader().hide()
        frozen.setEditTriggers(QAbstractItemView.NoEditTriggers)
        frozen.setSelectionMode(QAbstractItemView.NoSelection)
        frozen.setFocusPolicy(QtCore.Qt.NoFocus)
        frozen.setShowGrid(False)
        frozen.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        frozen.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        frozen.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._apply_style(frozen)
        # A subtle right edge separates the frozen column from the scrolling area.
        set_stylesheet(frozen, css("QTableView", border_right=f"1px solid {Style.Color.BorderElevated}", background=Style.Color.Background))

        for c in range(model.columnCount()):
            frozen.setColumnHidden(c, c != self._frozen_column)

        self.viewport().stackUnder(frozen)  # draw the frozen column on top of the scroll area

        # Vertical scroll is shared in both directions.
        self.verticalScrollBar().valueChanged.connect(frozen.verticalScrollBar().setValue)
        frozen.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        # Keep the frozen width in sync if the user drags the ID column wider.
        self.horizontalHeader().sectionResized.connect(self._on_section_resized)

        frozen.show()

    def _on_section_resized(self, logical_index, _old, new_size):
        if logical_index == self._frozen_column:
            self.frozen.setColumnWidth(self._frozen_column, new_size)
            self._update_frozen_geometry()

    def _update_frozen_geometry(self):
        frame = self.frameWidth()
        self.frozen.horizontalHeader().setFixedHeight(self.horizontalHeader().height())
        self.frozen.setColumnWidth(self._frozen_column, self.columnWidth(self._frozen_column))
        self.frozen.setGeometry(
            frame,
            frame,
            self.columnWidth(self._frozen_column),
            self.viewport().height() + self.horizontalHeader().height(),
        )

    def sync_row_heights(self):
        for r in range(self.model().rowCount()):
            self.frozen.setRowHeight(r, self.rowHeight(r))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_frozen_geometry()

    def wheelEvent(self, event):
        # Spec: horizontal scroll with the mouse wheel while hovering over the header.
        pos = event.position().toPoint()
        if pos.y() < self.horizontalHeader().height():
            delta = event.angleDelta().y() / 2
            scrollbar = self.horizontalScrollBar()
            scrollbar.setValue(scrollbar.value() - int(delta))
            event.accept()
        else:
            super().wheelEvent(event)


class TablePopup(QWidget):
    def __init__(self, parent, model, frozen_column: int = 0):
        # Cover the whole top-level window (main + side panel) so clicking anywhere
        # outside the table -- including the side panel -- closes the popup.
        window = parent.window()
        super().__init__(window, QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(window.rect())
        self._model = model

        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        set_stylesheet(overlay, css(background_color=Style.Color.Overlay))
        overlay.show()

        self.popup = QFrame(self)
        w, h = int(window.width() * 0.95), int(window.height() * 0.95)
        self.popup.setFixedSize(w, h)
        self.popup.move((window.width() - w) // 2, (window.height() - h) // 2)
        set_stylesheet(self.popup, css(background=Style.Color.Background))
        self.popup.mousePressEvent = lambda e: e.accept()

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(5, 5, 5, 5)
        popup_layout.setSpacing(5)

        popup_layout.addWidget(self._build_options_bar())

        self.table = DataTableView(model, frozen_column)
        popup_layout.addWidget(self.table)

        self.width_combo.currentIndexChanged.connect(self._relayout)
        self.wrap_checkbox.stateChanged.connect(self._relayout)
        self._relayout()

        self.raise_()
        self.show()
        # Take keyboard focus so Escape closes the popup (same outcome as clicking outside).
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()

    def _build_options_bar(self) -> QWidget:
        bar = QWidget(self.popup)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Columns:", bar))
        self.width_combo = QComboBox(bar)
        self.width_combo.addItems(["Fixed width", "Standard widths", "Fit content"])
        self.width_combo.setCurrentIndex(_MODE_FIXED)  # default: uniform medium width
        layout.addWidget(self.width_combo)

        self.wrap_checkbox = QCheckBox("Wrap text", bar)
        self.wrap_checkbox.setChecked(False)  # default: wrap on
        layout.addWidget(self.wrap_checkbox)

        layout.addStretch(1)
        return bar

    def _relayout(self, *args):
        mode = self.width_combo.currentIndex()
        wrap = self.wrap_checkbox.isChecked()
        table = self.table
        frozen = table.frozen
        model = self._model

        for view in (table, frozen):
            view.setWordWrap(wrap)
            view.setTextElideMode(QtCore.Qt.ElideNone if wrap else QtCore.Qt.ElideRight)
            view.horizontalHeader().set_wrap(wrap)

        # Column widths: Fixed = uniform medium; Standard = content clamped 80-300; Fit = content.
        if mode != _MODE_FIXED:
            table.resizeColumnsToContents()
        # Make sure content-based widths are available for the always-fit ID column even in
        # Fixed mode (which otherwise skips the content measurement above).
        if mode == _MODE_FIXED:
            table.resizeColumnToContents(table._frozen_column)
        widths = {}
        for c in range(model.columnCount()):
            if c == table._frozen_column:
                # The ID column always fits its content (it is the frozen column and never
                # benefits from a uniform/standard width), accounting for the painted header.
                widths[c] = max(table.columnWidth(c), self._header_content_width(c, wrap))
            elif mode == _MODE_FIXED:
                widths[c] = _FIXED_WIDTH
            elif mode == _MODE_FIT:
                # resizeColumnsToContents ignores the icon + paddings the custom header paints,
                # so a long column name would be clipped on the right. Ensure the column is at
                # least as wide as the painted header content.
                widths[c] = max(table.columnWidth(c), self._header_content_width(c, wrap))
            else:  # standard
                widths[c] = max(_STANDARD_MIN_WIDTH, min(table.columnWidth(c), _STANDARD_MAX_WIDTH))
            table.setColumnWidth(c, widths[c])
        frozen.setColumnWidth(table._frozen_column, widths.get(table._frozen_column, _STANDARD_MIN_WIDTH))

        # Header height: grows to fit wrapped names; single line otherwise.
        header_height = self._compute_header_height(wrap, widths)
        table.horizontalHeader().setFixedHeight(header_height)
        frozen.horizontalHeader().setFixedHeight(header_height)

        # Row heights follow the (possibly wrapped) cell content, then mirror to the frozen view.
        table.resizeRowsToContents()
        table.sync_row_heights()
        table._update_frozen_geometry()

    def _header_content_width(self, column: int, wrap: bool) -> int:
        """Width the custom header needs to paint its content without clipping: the column
        name plus left/right padding (4+4, matching paintSection's text_rect) and, when an
        icon is present, the icon width plus its gap (_ICON_SIZE + 4)."""
        model = self._model
        column_type = model.headerData(column, QtCore.Qt.Horizontal, TYPE_ROLE)
        icon_width = (_ICON_SIZE + 4) if COLUMN_TYPE_ICONS.get(column_type) is not None else 0
        chrome = 8 + icon_width
        if wrap:
            # When wrapping, the name flows over multiple lines, so the icon + paddings alone
            # set the minimum horizontal footprint.
            return chrome + _ICON_SIZE
        name = str(model.headerData(column, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole))
        metrics = QtGui.QFontMetrics(self.table.horizontalHeader().font())
        return metrics.horizontalAdvance(name) + chrome + 2

    def _compute_header_height(self, wrap, widths) -> int:
        header = self.table.horizontalHeader()
        metrics = QtGui.QFontMetrics(header.font())
        base = metrics.height() + 10
        if not wrap:
            return base
        max_height = base
        model = self._model
        for c in range(model.columnCount()):
            name = str(model.headerData(c, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole))
            available = max(10, widths.get(c, _STANDARD_MIN_WIDTH) - _ICON_SIZE - 12)
            bounds = metrics.boundingRect(QtCore.QRect(0, 0, available, 10000), QtCore.Qt.TextWordWrap, name)
            max_height = max(max_height, bounds.height() + 10)
        return max_height

    def mousePressEvent(self, event):
        if not self.popup.geometry().contains(event.position().toPoint()):
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)

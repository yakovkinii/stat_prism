#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import colorsys
import json
import logging
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile

import openpyxl
import pandas as pd
from PySide6 import QtWidgets

from src.common.constant import ColumnType, ID_COLUMN_NAME, argb_to_hex
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data import Data, DataColumn
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.raw_data.raw_data_result import RawDataStudyConfig

_DRAWING_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
# The clrScheme XML lists colours as dk1, lt1, dk2, lt2, accent1..6, hlink, folHlink, but the
# spreadsheet "theme" index swaps the first two pairs (0=lt1, 1=dk1, 2=lt2, 3=dk2, ...).
_THEME_INDEX_ORDER = [1, 0, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11]
_JAMOVI_INT_MISSING = -(2**31)


def _parse_theme_colors(theme_xml) -> list:
    """Extract the workbook theme's base palette as a list of '#rrggbb', ordered by the
    spreadsheet 'theme' index. Empty list if the theme is missing/unparseable."""
    if not theme_xml:
        return []
    try:
        if isinstance(theme_xml, bytes):
            theme_xml = theme_xml.decode("utf-8", "ignore")
        root = ET.fromstring(theme_xml)
        scheme = root.find(f".//{_DRAWING_NS}clrScheme")
        if scheme is None:
            return []
        scheme_colors = []
        for child in scheme:
            srgb = child.find(f"{_DRAWING_NS}srgbClr")
            sys_clr = child.find(f"{_DRAWING_NS}sysClr")
            if srgb is not None:
                scheme_colors.append("#" + srgb.get("val", "000000").lower())
            elif sys_clr is not None:
                scheme_colors.append("#" + (sys_clr.get("lastClr") or "000000").lower())
        if len(scheme_colors) < 12:
            return []
        return [scheme_colors[i] for i in _THEME_INDEX_ORDER]
    except ET.ParseError:
        return []


def _apply_tint(hex_color: str, tint: float) -> str:
    """Apply an OOXML tint (lighten/darken) to '#rrggbb' via HSL luminance, per ECMA-376."""
    if not tint:
        return hex_color
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l * (1 + tint) if tint < 0 else l * (1 - tint) + tint
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s)
    return f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}"


def _resolve_fill_color(fg_color, theme_colors: list):
    """Resolve an openpyxl fill fgColor to '#rrggbb': literal RGB directly, theme-palette
    colours via the parsed theme + tint. Indexed/auto colours return None (skipped)."""
    color_type = getattr(fg_color, "type", None)
    if color_type == "theme":
        index = getattr(fg_color, "theme", None)
        if isinstance(index, int) and 0 <= index < len(theme_colors):
            return _apply_tint(theme_colors[index], getattr(fg_color, "tint", 0.0) or 0.0)
        return None
    rgb = getattr(fg_color, "rgb", None)
    return argb_to_hex(rgb) if isinstance(rgb, str) else None


def _read_null_terminated_string(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    if end == -1:
        end = len(data)
    return data[offset:end].decode("utf-8", "replace")


def _jamovi_label_map(column_name: str, xdata: dict) -> dict:
    """Return {raw_value: display_label} for a jamovi column, if labels are present."""
    labels = xdata.get(column_name, {}).get("labels", []) if isinstance(xdata, dict) else []
    mapping = {}
    for label in labels:
        if not isinstance(label, list) or len(label) < 2:
            continue
        raw_value, display_label = label[0], label[1]
        mapping[raw_value] = display_label
        mapping[str(raw_value)] = display_label
        if isinstance(raw_value, float) and raw_value.is_integer():
            mapping[int(raw_value)] = display_label
            mapping[str(int(raw_value))] = display_label
    return mapping


def _apply_jamovi_labels(values: list, column_name: str, xdata: dict) -> list:
    mapping = _jamovi_label_map(column_name, xdata)
    if not mapping:
        return values
    return [None if pd.isna(value) else mapping.get(value, mapping.get(str(value), value)) for value in values]


def _jamovi_column_type(field: dict):
    measure_type = field.get("measureType")
    if measure_type == "ID":
        return ColumnType.NOMINAL
    if measure_type == "Nominal":
        return ColumnType.NOMINAL
    if measure_type == "Ordinal":
        return ColumnType.ORDINAL
    if measure_type == "Continuous":
        return ColumnType.NUMERIC
    return None


def _jamovi_order(column_name: str, xdata: dict) -> dict:
    mapping = _jamovi_label_map(column_name, xdata)
    if not mapping:
        return {}
    ordered_values = []
    labels = xdata.get(column_name, {}).get("labels", [])
    for label in labels:
        if not isinstance(label, list) or len(label) < 2:
            continue
        display_label = label[1]
        if display_label not in ordered_values:
            ordered_values.append(display_label)
    return {value: index for index, value in enumerate(ordered_values, start=1)}


def _read_jamovi_omv(file_path: str):
    """Read the tabular data from a jamovi .omv archive.

    jamovi stores the table as column metadata plus binary column vectors. This handles the
    core saved-data types used by jamovi: integer, number, and string columns. Analysis
    output and transforms are intentionally ignored; StatPrism imports the saved data table.
    """
    with zipfile.ZipFile(file_path, "r") as archive:
        metadata = json.loads(archive.read("metadata.json").decode("utf-8"))["dataSet"]
        try:
            xdata = json.loads(archive.read("xdata.json").decode("utf-8"))
        except KeyError:
            xdata = {}
        data_bytes = archive.read("data.bin")
        strings_bytes = archive.read("strings.bin") if "strings.bin" in archive.namelist() else b""

    row_count = int(metadata["rowCount"])
    fields = metadata.get("fields", [])
    if len(fields) != int(metadata["columnCount"]):
        raise ValueError("Jamovi metadata column count does not match the field list.")

    offset = 0
    columns = {}
    column_metadata = {}
    for field in fields:
        column_name = field["name"]
        column_type = field.get("type")

        if column_type == "integer":
            byte_count = 4 * row_count
            values = list(struct.unpack(f"<{row_count}i", data_bytes[offset : offset + byte_count]))
            offset += byte_count
            values = [None if value == _JAMOVI_INT_MISSING else value for value in values]
        elif column_type == "number":
            byte_count = 8 * row_count
            values = list(struct.unpack(f"<{row_count}d", data_bytes[offset : offset + byte_count]))
            offset += byte_count
        elif column_type == "string":
            byte_count = 4 * row_count
            indexes = struct.unpack(f"<{row_count}i", data_bytes[offset : offset + byte_count])
            offset += byte_count
            values = [
                None
                if index == _JAMOVI_INT_MISSING
                else _read_null_terminated_string(strings_bytes, index)
                for index in indexes
            ]
        else:
            raise ValueError(f"Unsupported jamovi column type: {column_type}")

        columns[column_name] = _apply_jamovi_labels(values, column_name, xdata)
        metadata = {}
        stat_prism_type = _jamovi_column_type(field)
        if stat_prism_type is not None:
            metadata["column_type"] = stat_prism_type
        if stat_prism_type == ColumnType.ORDINAL:
            metadata["order"] = _jamovi_order(column_name, xdata)
        if metadata:
            column_metadata[column_name] = metadata

    return pd.DataFrame(columns), column_metadata


class RawData(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "open": LargeButton(
                label_text="Replace Data",
                icon_path="ph.arrows-clockwise",
            ),
        }
        self.setup(stretch=True, label="Load Raw Data")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        pass

    def _build_data(self, config: RawDataStudyConfig) -> Data:
        data = Data.initialize_from_dataframe(config.dataframe.copy())
        if data.n_columns() > 0:
            for column in data.columns:
                metadata = (config.column_metadata or {}).get(column.column_name, {})
                column_type = metadata.get("column_type")
                if column_type is not None:
                    column.column_type = column_type
                    column.is_numeric = column_type == ColumnType.NUMERIC
                if column.column_type == ColumnType.ORDINAL:
                    column.order = metadata.get("order") or {}
                    column.automatically_update_order()
                elif column.column_type not in (ColumnType.NOMINAL, ColumnType.ORDINAL):
                    column.order = {}
            # Apply colour tags read from the source sheet's coloured header cells.
            for name, color in (config.header_colors or {}).items():
                if name in data.column_names():
                    data[name].color = color
            # A mandatory identifier column, always named exactly ID_COLUMN_NAME and typed as ID.
            # If the loaded data already has such a column, rename that existing one out of the way.
            if ID_COLUMN_NAME in data.column_names():
                data.rename_column(ID_COLUMN_NAME, unique_name(ID_COLUMN_NAME, set(data.column_names())))
            index = data.columns[0].data_series.index
            id_series = pd.Series(range(1, len(index) + 1), index=index, name=ID_COLUMN_NAME)
            id_column = DataColumn.initialize_from_series(id_series)
            id_column.column_type = ColumnType.ID
            id_column.is_numeric = False
            data.add_column_first(id_column)
        return data

    @staticmethod
    def _read_header_colors(file_path, sheet_name) -> dict:
        """Read fill colours of the header row (row 1) of an .xlsx sheet, keyed by header text.
        Handles both literal RGB fills and theme-palette fills (the standard Excel colour grid,
        resolved to RGB via the workbook theme + tint). Indexed/auto colours are skipped."""
        if not file_path.lower().endswith(".xlsx"):
            return {}
        try:
            workbook = openpyxl.load_workbook(file_path)
            worksheet = workbook[sheet_name] if sheet_name not in (0, None) else workbook.worksheets[0]
            theme_colors = _parse_theme_colors(getattr(workbook, "loaded_theme", None))
            colors = {}
            for cell in worksheet[1]:
                if cell.value is None:
                    continue
                fill = cell.fill
                if fill is None or fill.patternType != "solid":
                    continue
                hex_color = _resolve_fill_color(fill.fgColor, theme_colors)
                if hex_color:
                    colors[str(cell.value)] = hex_color
            return colors
        except Exception as e:
            logging.warning(f"Could not read header colours from {file_path}: {e}")
            return {}

    @log_method_noarg
    def open_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.omv *.xlsx *.csv);;All Files (*)",
        )
        if not file_path:
            logging.info("No file selected")
            return
        self.open_file(file_path)

    def _choose_sheet(self, file_path):
        """For a multi-sheet .xlsx, ask which sheet to load. Returns the chosen sheet name,
        0 (first/only sheet, no prompt) for single-sheet or non-Excel files, or False if the
        user cancelled the picker."""
        if not file_path.lower().endswith(".xlsx"):
            return 0
        sheets = pd.ExcelFile(file_path).sheet_names
        if len(sheets) <= 1:
            return 0
        name, ok = QtWidgets.QInputDialog.getItem(
            self.widget, "Select sheet", "Worksheet:", sheets, 0, False
        )
        return name if ok else False

    @log_method
    def open_file(self, file_path):
        # Sheet selection happens here (on the main thread, before the worker starts) so every
        # entry point -- "Replace Data", first open, and sample load -- gets the same prompt.
        sheet_name = self._choose_sheet(file_path)
        if sheet_name is False:  # multi-sheet workbook but the user cancelled the picker
            return

        def main(update):
            logging.info(f"Opening {file_path}")
            update(10)
            column_metadata = {}
            extension = Path(file_path).suffix.lower()
            if extension == ".csv":
                dataframe = pd.read_csv(file_path)
            elif extension == ".xlsx":
                dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
            elif extension == ".omv":
                dataframe, column_metadata = _read_jamovi_omv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            update(80)
            config = RawDataStudyConfig(
                dataframe=dataframe,
                path=Path(file_path).resolve(),
                timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                header_colors=self._read_header_colors(file_path, sheet_name),
                column_metadata=column_metadata,
            )
            return config

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.open_file_on_done
        )

    @log_method
    def open_file_on_done(self, config):
        RESULTS[self.result_id].config = config
        RESULTS[self.result_id].data = self._build_data(config)
        DATA_MANAGER.set_raw_data_result_id(self.result_id)
        self.root_class.main_area_panel.refresh_result(self.result_id)
        self.root_class.main_area_panel.cascade_update(self.result_id)
        self.root_class.set_current_file_path(None)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                self.open_handler()
            return
        super().handler(message)

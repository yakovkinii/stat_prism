#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import List

from src.common.constant import TABLE_OR_PLOT_ID_PLACEHOLDER
from src.common.decorators import log_method_noarg
from src.common.translations import t
from src.pyside_ext.elements.base import BasePanelElement
from src.side_area_panel.modules.common.result.base_result import BaseResultElement
from src.side_area_panel.panels.result_item_settings_classes import (
    ContainerResultItemSetting,
    SingleLineTextResultItemSetting,
)


class Cell:
    def __init__(
        self,
        text: any = "",
        is_bold: bool = False,
        is_italic: bool = False,
        border_left: bool = False,
        border_right: bool = False,
        border_top: bool = False,
        border_bottom: bool = False,
        col_span: int = 1,
        row_span: int = 1,
        push_to_right: bool = False,
        push_to_left: bool = False,
        center: bool = True,
        is_doubled: bool = False,
        no_wrap: bool = False,
    ):
        self.text = str(text)
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.border_left = border_left
        self.border_right = border_right
        self.border_top = border_top
        self.border_bottom = border_bottom
        self.col_span = col_span
        self.row_span = row_span
        self.push_to_right = push_to_right
        self.push_to_left = push_to_left
        self.center = center if not (push_to_left or push_to_right) else False
        self.is_doubled = is_doubled
        self.no_wrap = no_wrap


class Row:
    def __init__(self, cells: List[Cell]):
        self.cells: List[Cell] = cells


class HTMLTableV2(BaseResultElement):
    settings_panel_index = None

    def __init__(
        self,
        rows: List[Row] = None,
        title="Table",
        border_top: bool = True,
        border_bottom: bool = True,
        table_caption="",
        table_note="",
        texts: List[str] = None,
    ):
        super().__init__()
        logging.info("Creating HTMLTableV2")
        self.title: str = title
        self.class_id: str = "HTMLTableV2"
        self.rows: List[Row] = rows if rows is not None else []
        self.border_top = border_top
        self.border_bottom = border_bottom
        self.table_note: str = table_note
        self.texts: List[str] = texts if texts is not None else []

        self.table_caption = SingleLineTextResultItemSetting(label="Title:", current_value=table_caption)

        self.display_settings = {
            "General": ContainerResultItemSetting(
                items=[self.table_caption],
                add_stretch=True,
            ),
        }

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("display_settings", None)
        state.pop("class_id", None)
        state.pop("_gc_ignore", None)

        for k, v in state.items():
            if issubclass(type(v), BasePanelElement):
                state[k] = v.get_current_value()
        logging.warning(f"HTMLTableV2 {state=}")
        return state

    def __setstate__(self, state):
        self.__init__(**state)

    def load_settings_from(self, table: "HTMLTableV2"):
        self.table_caption.set_up_from_other_instance(table.table_caption)

    @log_method_noarg
    def get_html(self, renderer=None):
        id_suffix = ""
        note_str = t("common.note")

        # Propagate top/bottom borders to cell flags
        if self.rows:
            if self.border_top:
                for cell in self.rows[0].cells:
                    cell.border_top = True
            if self.border_bottom:
                for cell in self.rows[-1].cells:
                    cell.border_bottom = True

        total_rows = len(self.rows)
        caption = self.table_caption.get_current_value()
        # Title rendered as a bold caption above the table (shown and copied with it).
        html = f'<div class="font"><b>{caption}</b></div>\n' if caption else ""
        if total_rows > 0:
            html += '<table style="border-collapse: collapse;" class="font">'

            for r_idx, row in enumerate(self.rows):
                html += "<tr>"
                for cell in row.cells:
                    # Base cell style with increased line-height
                    cell_style = "padding: 5px;"
                    if cell.is_bold:
                        cell_style += " font-weight: bold;"
                    if cell.is_italic:
                        cell_style += " font-style: italic;"
                    if cell.no_wrap:
                        cell_style += " white-space: nowrap;"
                    if cell.push_to_right:
                        cell_style += " text-align: right;"
                    elif cell.push_to_left:
                        cell_style += " text-align: left;"
                    elif cell.center:
                        cell_style += " text-align: center;"

                    # Top border
                    if r_idx == 0 and self.border_top:
                        cell_style += " border-top: 2px solid black;"
                    elif cell.border_top:
                        cell_style += " border-top: 1px solid black;"
                    # Bottom border
                    if r_idx == total_rows - 1 and self.border_bottom:
                        cell_style += " border-bottom: 2px solid black;"
                    elif cell.border_bottom:
                        cell_style += " border-bottom: 1px solid black;"

                    # Span
                    attrs = ""
                    if cell.col_span > 1:
                        attrs += f' colspan="{cell.col_span}"'
                    if cell.row_span > 1:
                        attrs += f' rowspan="{cell.row_span}"'

                    html += f'<td style="{cell_style}"{attrs}>{cell.text}</td>'
                html += "</tr>"
            html += "</table>\n"

            # Note
            if self.table_note:
                html += f'<div class="font"><i>{note_str}.</i> {self.table_note}</div>\n'

        # Additional texts
        for i, text in enumerate(self.texts):
            if (total_rows > 0) or (i > 0):
                html += "<br><br>\n"
            html += f'<div class="font">{text.replace(TABLE_OR_PLOT_ID_PLACEHOLDER, id_suffix)}</div><br>\n'
        return html

    def add_title_row_apa(self, row: Row):
        for cell in row.cells:
            cell.border_bottom = True
        self.rows.append(row)

    def add_single_row_apa(self, row: Row):
        self.rows.append(row)

    def add_multirow_apa(self, rows: List[Row]):
        for cell in rows[0].cells:
            cell.border_top = True
        for row in rows:
            self.rows.append(row)

    def add_text(self, text=None):
        self.texts.append(text)

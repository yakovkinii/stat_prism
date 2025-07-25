#  Copyright (c) 2023 StatPrism Team. All rights reserved.




import logging
from typing import List

from src.common.constant import TABLE_OR_PLOT_ID_PLACEHOLDER
from src.common.decorators import log_method, log_method_noarg
from src.common.languages import LANGUAGE
from src.common.result.base_result import BaseResultElement
from src.settings_panel.panels.result_item_settings_v2.classes import NumberCaptionResultItemSetting, \
    SingleLineTextResultItemSetting, ContainerResultItemSetting


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
        tab_title="Table",
        border_top: bool = True,
        border_bottom: bool = True,
        table_id="",
        table_caption="(Table caption)",
        table_note="",
        texts: List[str] = None,
    ):
        super().__init__()
        logging.info("Creating HTMLTableV2")
        self.title: str = tab_title
        self.class_id: str = "HTMLTableV2"
        self.rows: List[Row] = rows if rows is not None else []
        self.border_top = border_top
        self.border_bottom = border_bottom
        self.table_note: str = table_note

        self.texts: List[str] = texts if texts is not None else []

        self.table_id = SingleLineTextResultItemSetting(label="Number:", current_value=table_id)
        self.table_caption = SingleLineTextResultItemSetting(label="Title:", current_value=table_caption)

        self.display_settings = {
            "General": ContainerResultItemSetting(
                items=[
                    self.table_id,
                    self.table_caption,
                ],
                add_stretch=True,
            ),
        }



    @log_method_noarg
    def get_html(self, renderer=None):
        table_id = self.table_id.get_current_value() + "." if self.table_id.get_current_value() != "" else ""

        table_str = "Таблиця" if LANGUAGE.is_ua() else "Table"
        note_str = "Нотатка" if LANGUAGE.is_ua() else "Note"

        # Caption
        html = ""
        html += f"""
            <div class="double-spacing font"><b>
            {table_str} {table_id}
            </b></div>
        """
        html += f'<div class="double-spacing font"><i>{self.table_caption.get_current_value()}</i></div><br>'

        style = ""
        if self.border_top:
            style += "border-top: 2px solid black;"
        if self.border_bottom:
            style += "border-bottom: 2px solid black;"

        html += f'<table style="{style}" class="font">'

        for row in self.rows:
            html += "<tr>"
            for cell in row.cells:
                style = "padding: 5px;"
                attributes = ""
                if cell.is_doubled:
                    style += "width: 40px;"
                else:
                    style += "width: 80px;"
                if cell.is_bold:
                    style += "font-weight: bold;"
                if cell.is_italic:
                    style += "font-style: italic;"
                if cell.border_left:
                    style += f"border-left: 1px solid black;"
                if cell.border_right:
                    style += f"border-right: 1px solid black;"
                if cell.border_top:
                    style += f"border-top: 1px solid black;"
                if cell.border_bottom:
                    style += f"border-bottom: 1px solid black;"
                if cell.col_span > 1:
                    attributes += f' colspan="{cell.col_span}"'
                if cell.row_span > 1:
                    attributes += f' rowspan="{cell.row_span}"'
                if cell.push_to_right:
                    style += "text-align: right; padding-right: 0px; margin-right:0px;"
                if cell.push_to_left:
                    style += "text-align: left; padding-left: 0px; margin-left:0px;"
                if cell.center:
                    style += "text-align: center;"
                if cell.no_wrap:
                    style += "white-space: nowrap;"
                html += f'<td style="{style}" {attributes}>{cell.text}</td>'
            html += "</tr>"
        html += "</table>\n"
        if self.table_note != "":
            html += f'<div class="double-spacing font"><i>{note_str}.</i> {self.table_note}</div>\n'

        for text in self.texts:
            html += (
                "<br><br>\n"
                f'<div class="double-spacing font"> \n'
                f"{text.replace(TABLE_OR_PLOT_ID_PLACEHOLDER, table_id)}\n"
                f"</div><br>\n"
            )
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

    @log_method
    def split_table(self, max_cols: int):  # Todo maybe return as multitable (group by as same tab)
        logging.warning("HTMLTableV2.split_table is deprecated")
        new_tables = []
        num_cols = len(self.rows[0].cells)

        if num_cols <= max_cols:
            return [self]

        for i in range(1, num_cols, max_cols):
            new_table = HTMLTableV2(
                rows=[Row(cells=[row.cells[0]] + row.cells[i : i + max_cols]) for row in self.rows],
                table_id=self.table_id.get_current_value(),
                table_caption=self.table_caption if i == 1 else "",
                table_note=self.table_note if i == 1 else "",
            )
            new_tables.append(new_table)

        return HTMLMultiTableV2(new_tables)


class HTMLMultiTableV2(BaseResultElement):
    def __init__(self, tables: List[HTMLTableV2], tab_title="Table"):
        logging.warning("HTMLMultiTableV2 is deprecated")
        super().__init__()
        logging.info("Creating HTMLMultiTableV2")
        self.title: str = tab_title
        self.class_id: str = "HTMLMultiTableV2"
        self.tables: List[HTMLTableV2] = tables
        self.table_id: str = tables[0].table_id
        self.table_caption: str = tables[0].table_caption

    @log_method_noarg
    def get_html(self, renderer=None):
        return "<br>".join([table.get_html() for table in self.tables])

    @log_method
    def set_table_id(self, table_id):
        for table in self.tables:
            table.set_table_id(table_id)

    @log_method
    def set_table_caption(self, table_caption):
        self.tables[0].set_table_caption(table_caption)

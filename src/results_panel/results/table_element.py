import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from src.results_panel.results.base_element import BaseResultElement


class TableResultElement(BaseResultElement):
    def __init__(self, dataframe, draw_index=False, color_values=True, title="Table Result Element"):
        super().__init__()
        self.title: str = title
        self.class_id: str = "TableResultElement"

        self.dataframe = dataframe
        self.draw_index = draw_index
        self.color_values = color_values


class TableResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: TableResultElement):
        self.result_element = result_element
        self.widget = QWidget(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(self.widget)

        html = self.get_html()
        self.label.setText(html)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.adjustSize()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addStretch()

    def get_html(self):
        if self.result_element.dataframe is None:
            return ""
        df = self.result_element.dataframe
        if self.result_element.draw_index:
            df = df.reset_index()

        min_max = {col: [df[col].min(), df[col].max()] for col in df.columns if np.issubdtype(df[col].dtype, np.number)}

        # df_non_numeric = df[[col for col in list(df.columns) if col not in min_max.keys()]]

        # category = {
        #     col: df_non_numeric[[col]].drop_duplicates().reset_index().set_index(col).rename(columns={"index": "id"})
        #     for col in df_non_numeric.columns
        #     if df_non_numeric[col].nunique() < 5
        # }

        header_style = '"font-weight:400;background-color:rgba(0,0,0,10); border: 1px solid #fff;"'

        html = "<table>"
        html += "<tr>"
        for column in df.columns:
            html += f'<td style={header_style}><span style="background-color:transparent">{column}</span></td>'
        html += "</tr>"

        for i, row in df.iterrows():
            html += "<tr>"
            for j, (column, value) in enumerate(row.items()):
                if j == 0:  # Row header
                    html += f'<td style={header_style}><span style="background-color:transparent">{value}</span></td>'

                else:
                    if column in min_max.keys():
                        color = self.color_for_value(value, min_max[column][0], min_max[column][1])
                    # elif column in category.keys():
                    #     color = self.color_for_category(category[value])
                    else:
                        color = "rgba(128,0,128,20)"
                    if not self.result_element.color_values:
                        color = "rgba(0,0,255,10)"
                    html += f'<td style="background-color: {color}; border: 1px solid #fff">'
                    html += f'<span style = "background-color: transparent">{value}</span'
                    html += "</td>"
            html += "</tr>"
        html += "</table>"

        # html_table = self.item.dataframe.to_html(index=False)
        html = CSS_STYLE + f'<div class="scrollable">{html}</div>'

        return html

    @staticmethod
    def color_for_value(value, min_value, max_value):
        if min_value == max_value:
            return "rgba(128,0,128,20)"
        intensity = int(255 * (value - min_value) / (max_value - min_value))
        return f"rgba({intensity}, 0, {255-intensity}, 20)"

    @staticmethod
    def color_for_category(id):
        colors = {
            "0": "rgba(255, 0, 0, 20)",
            "1": "rgba(0, 128, 0, 20)",
            "2": "rgba(0, 0, 255, 20)",
            "3": "rgba(255, 165, 0, 20)",
            "4": "rgba(128, 0, 128, 20)",
        }
        return colors[id]


CSS_STYLE = """
      <style>
      table, th, td, span {
        border-collapse: collapse;
        text-align: left;
        font-size: 14px;
        font-family: 'Segoe UI', Arial, sans-serif;
        border: 1px solid #000;
      }
      table{
      margin-bottom: 5px;
      margin-top: 5px;
      }

      td {
        padding: 5px 10px;
      }
      .scrollable {
        overflow-x: auto;
      }
      .thick-border-bottom{
        border-bottom: 2px solid #000;
      }
      .thick-border-top{
        border-top: 2px solid #000;
      }
      .thin-border-left{
        /*border-left: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-right{
        /*border-right: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-top{
        /*border-top: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-bottom{
        /*border-bottom: 1px solid rgba(0,0,0,10);*/
      }
      .align-right {
        text-align: right;
        padding-right: 0px;
        margin:0px;
      }
      .align-left {
        text-align: left;
        padding-left: 0px;
      }
      .footnote{
        text-align: left;
        margin-left: 10px;
        font-size: 12px;
        font-family: 'Segoe UI', Arial, sans-serif;
      }
      .table-name-apa{
        text-align: left;
        margin-left: 0px;
        margin-top:3px;
        margin-bottom:3px;
        font-size: 14px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
      }
      .table-title-apa{
        text-align: left;
        margin-left: 0px;
        margin-top:3px;
        font-size: 14px;
        font-style: italic;
        font-family: 'Segoe UI', Arial, sans-serif;
      }
      .nowrap{
      white-space: nowrap;
      }
      .multilinemm {
        width: 20px; /* Adjust the width as needed */
        word-wrap: break-word;
        white-space: normal; /* Override any existing nowrap */
      }
      </style>
      """

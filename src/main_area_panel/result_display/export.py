#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import pandas as pd
from openpyxl.styles import PatternFill
from PySide6.QtWidgets import QFileDialog

from src.common.constant import hex_to_argb


def export_data_to_excel(parent_widget, data):
    """Prompt for a path and write `data` to .xlsx, painting each header cell with its
    column's colour tag. Shared by the Raw Data and data-processing result cards."""
    if data is None or data.n_columns() == 0:
        logging.info("No data to export")
        return

    file_path, _ = QFileDialog.getSaveFileName(parent_widget, "Export to Excel", "", "Excel files (*.xlsx)")
    if not file_path:
        return
    if not file_path.endswith(".xlsx"):
        file_path += ".xlsx"

    try:
        df = data.get_dataframe()
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            worksheet = writer.sheets["Sheet1"]
            # Paint each header cell with its column's colour tag (row 1; openpyxl is 1-based).
            for col_index, name in enumerate(df.columns, start=1):
                argb = hex_to_argb(data[name].color)
                if argb:
                    worksheet.cell(row=1, column=col_index).fill = PatternFill(fill_type="solid", fgColor=argb)
    except Exception as e:
        logging.error(f"Failed to export data to Excel: {e}")

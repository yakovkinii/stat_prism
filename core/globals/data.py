from typing import List

import pandas as pd

from core.registry.utility import log_method


class ColumnInfo:
    def __init__(self, full_name, display_name):
        self.full_name = full_name
        self.display_name = display_name
        self.width = 180
        self.category = None
        self.folded_group = None


class Data:
    def __init__(self, df: pd.DataFrame = None):
        self.folded_groups = []
        self.filter = None
        self.df = None
        self.column_info = None
        self.load(df)

    @log_method
    def load(self, df: pd.DataFrame = None):
        self.filter = None
        self.folded_groups = []

        if df is None:
            self.df = None
            self.column_info = None
        else:
            self.df = df
            self.column_info: List[ColumnInfo] = []
            for column in df.columns:
                self.column_info.append(
                    ColumnInfo(full_name=str(column), display_name=self.format_string(str(column), 20, 8))
                )

    @log_method
    def format_string(self, input_string, max_row_length, max_rows):
        words = input_string.split()
        current_line = ""
        result = ""
        n_lines = 0
        for word in words:
            # Check if adding the next word would exceed the max row length
            if len(current_line) + len(word) + 1 > max_row_length:
                # Append the current line to the result and reset current_line
                n_lines += 1
                if n_lines == max_rows:
                    if len(current_line) > max_row_length - 3:
                        current_line = current_line[:, max_row_length - 3]
                    return result + current_line + "..."

                result += current_line + "\n"

                current_line = word
            else:
                # Add the word to the current line
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        # Add the last line to the result if it's not empty
        if current_line:
            result += current_line

        return result

from src.common.result.classes.html_result import Cell, HTMLTable, Row
from src.common.utility import smart_comma_join


def get_table_compact(columns, crosstab_matrix) -> HTMLTable:
    table = HTMLTable([])
    crosstab_matrix = crosstab_matrix.reset_index()

    table.table_id = "1"
    table.table_caption = "Crosstab between " + smart_comma_join([f"'{var}'" for var in columns]) + "."

    # Add header
    table.add_title_row_apa(Row([Cell(column, center=True) for column in crosstab_matrix.columns]))

    # Add matrix
    for row_name, row in crosstab_matrix.iterrows():
        table_row = []
        for column in row:
            table_row.append(
                Cell(
                    column,
                    push_to_right=True,
                    is_doubled=True,
                    no_wrap=True,
                )
            )

        table.add_single_row_apa(Row(table_row))

    return table

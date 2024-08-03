from src.common.utility import smart_comma_join
from src.results_panel.results.common.html_element import Cell, HTMLTable, Row


def get_table_compact(columns, ordnallogregression_matrix) -> HTMLTable:
    table = HTMLTable([])
    ordnallogregression_matrix = ordnallogregression_matrix.reset_index()

    table.table_id = "1"
    table.table_caption = "Ordnallogregression between " + smart_comma_join([f"'{var}'" for var in columns]) + "."

    # Add header
    table.add_title_row_apa(Row([Cell(column, center=True) for column in ordnallogregression_matrix.columns]))

    # Add matrix
    for row_name, row in ordnallogregression_matrix.iterrows():
        table_row = [Cell(row_name)]
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

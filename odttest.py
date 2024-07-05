import pandas as pd
from odf.opendocument import OpenDocumentText
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.style import Style, TableCellProperties, TableColumnProperties, TableRowProperties, TextProperties

# Sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)


def create_odt_from_dataframe(df, filename, header_colors=None, cell_colors=None):
    doc = OpenDocumentText()

    # Define styles for header and cells
    styles = {}
    if header_colors:
        for col, color in header_colors.items():
            style_name = f"HeaderStyle_{col}"
            styles[col] = Style(name=style_name, family="table-cell")
            styles[col].addElement(TableCellProperties(backgroundcolor=color))
            doc.styles.addElement(styles[col])

    if cell_colors:
        for (row_idx, col_idx), color in cell_colors.items():
            style_name = f"CellStyle_{row_idx}_{col_idx}"
            styles[(row_idx, col_idx)] = Style(name=style_name, family="table-cell")
            styles[(row_idx, col_idx)].addElement(TableCellProperties(backgroundcolor=color))
            doc.styles.addElement(styles[(row_idx, col_idx)])

    # Create table
    table = Table()

    # Add columns to the table
    for _ in range(len(df.columns)):
        table.addElement(TableColumn())

    # Add header row with styles
    header_row = TableRow()
    for col in df.columns:
        cell = TableCell()
        p = P(text=col)
        cell.addElement(p)
        if header_colors and col in header_colors:
            cell.setAttribute("stylename", styles[col].getAttribute("name"))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Add data rows with styles
    for row_idx, row in df.iterrows():
        table_row = TableRow()
        for col_idx, (col_name, cell_data) in enumerate(row.items()):
            cell = TableCell()
            p = P(text=str(cell_data))
            cell.addElement(p)
            if cell_colors and (row_idx, col_idx) in cell_colors:
                cell.setAttribute("stylename", styles[(row_idx, col_idx)].getAttribute("name"))
            table_row.addElement(cell)
        table.addElement(table_row)

    # Append table to the document
    doc.text.addElement(table)

    # Save the document
    doc.save(filename)


# Define colors for headers and specific cells
header_colors = {
    'Name': "#FFCCCC",
    'Age': "#CCFFCC"
}
cell_colors = {
    (1, 1): "#FFFF99",  # Bob's Age
    (2, 2): "#99CCFF"  # Charlie's City
}

# Usage
create_odt_from_dataframe(df, './output_test.odt', header_colors, cell_colors)

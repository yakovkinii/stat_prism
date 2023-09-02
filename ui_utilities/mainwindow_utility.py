from PyQt5.QtWidgets import QTableWidgetItem


def load_data_to_table(dataframe, table_widget):
    table_widget.setRowCount(dataframe.shape[0])
    table_widget.setColumnCount(dataframe.shape[1])
    table_widget.setHorizontalHeaderLabels(dataframe.columns)

    for row in dataframe.iterrows():
        for col, value in enumerate(row[1]):
            table_widget.setItem(row[0], col, QTableWidgetItem(str(value)))


def get_html_start_end():
    html_start = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Page Title</title>
        <style>
            /* Base Table Styles */
            table {
                border-collapse: collapse;
                font-size: 18px;
                width: 100%;
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                text-align: right;
            }

            th, td {
                padding: 8px 12px;
                border: 1px solid #ddd;
                width: 50px;
                min-width: 50px;
                position:relative;
            }

            th {
                background-color: #f7f9fa;
            }

            tr:hover {
                background-color: #e5f3f8;
            }

            /* Freeze the first column */
            td:first-child, th:first-child {
                position: sticky;
                left: 0;
                z-index: 1;
                font-weight:800;
                background-color: #f7f9fa;
            }
            .hidden_first_th th:first-child {{
                visibility: hidden;
            }}
        </style>
    </head>

    <body>
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center; width:100%;">
        """
    html_end = """
    </div>
    </body>
    </html>
    """
    return html_start, html_end


def div_title():
    return (f'<div style="font-size:32px;text-align:center; font-family: \'Open Sans\'; color:#000077;'
            + f'font-weight: 500;margin:20px;">')


def div_text():
    return (f'<div style="font-size:24px;text-align:justify; font-family: \'Open Sans\'; color:#000077;'
            + f'font-weight: 500;margin:20px;">')


def div_table():
    return (f'<div style="font-size:24px;text-align:justify; font-family: \'Open Sans\'; color:#000077;'
            + f'font-weight: 500;margin:20px;overflow:auto;width:100%;">')


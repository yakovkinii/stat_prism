HOME_INDEX = 0
OUTPUT_WIDTH = 700

NO_RESULT_SELECTED = -1
ALL_STUDIES_INDEXES = [1]

DESCRIPTIVE_MODEL_NAME = "Descriptive model"
CORRELATION_MODEL_NAME = "Correlation model"


def add_checkbox_to_groupbox(groupBox, i, formLayout):
    checkbox = QtWidgets.QCheckBox(groupBox)
    checkbox.setChecked(True)
    formLayout.setWidget(i, QtWidgets.QFormLayout.LabelRole, checkbox)
    return checkbox


def create_tool_button(parent, button_geometry, icon_path, icon_size):
    button = QtWidgets.QToolButton(parent)
    button.setGeometry(button_geometry)
    button.setText("")
    button.setIcon(icon(icon_path))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    return button


class VerticalLayout(QLayout):
    def __init__(
        self, parent, padding_left=0, padding_right=0, padding_top=0, padding_bottom=0, spacing=0, top_level=False
    ):
        super().__init__(parent)
        self.parent = parent
        self.top_level = top_level
        self.padding_left = padding_left
        self.padding_right = padding_right
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.spacing = spacing
        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def setGeometry(self, rect):
        super(VerticalLayout, self).setGeometry(rect)
        if self.count() == 0:
            return
        y = rect.y() + self.padding_top
        x = rect.x() + self.padding_left
        for item in self.items:
            widget_height = item.sizeHint()._height()
            item.setGeometry(QRect(x, y, rect.width() - self.padding_left - self.padding_right, widget_height))
            y += widget_height + self.spacing

    def sizeHint(self):
        if self.top_level:
            return self.parent.size()
        if len(self.items) == 0:
            return QSize(self.padding_left + self.padding_right, self.padding_top + self.padding_bottom)
        height = self.padding_top + self.padding_bottom + self.spacing * (len(self.items) - 1)
        height += sum(item.sizeHint()._height() for item in self.items)
        width = max(item.sizeHint().width() for item in self.items) + self.padding_left + self.padding_right
        return QSize(width, height)


class Result:
    def __init__(self, result_id: int, module_name: str):
        self.result_id = result_id
        self.module_name = module_name
        self.items: List[TextResultItem, TableResultItem] = ...
        self.metadata = ...
        self.title = ""


class TextResultItem:
    def __init__(self, text: str, title: str = None):
        self.type = "TextResultItem"
        self.title = title
        self.text = text


class TableResultItem:
    def __init__(
        self,
        dataframe: pd.DataFrame = None,
        title: str = None,
        draw_index=False,
        color_values=True,
    ):
        self.type = "TableResultItem"
        self.title = title
        self.dataframe = dataframe
        self.draw_index = draw_index
        self.color_values = color_values
        self.html = None


class PlotResultItem:
    def __init__(self, dataframe: pd.DataFrame, title: str = None):
        self.type = "PlotResultItem"
        self.title = title
        self.dataframe = dataframe
        self.x_axis_title = ""
        self.y_axis_title = ""


class ResultContainer:
    def __init__(self):
        self.results: Dict[int, Result] = dict()
        self.current_result = NO_RESULT_SELECTED


class ModelRegistryItem:
    def __init__(
        self,
        model_name: str,
        stacked_widget_index: int,
        setup_from_result_handler: Callable,
        run_handler: Callable,
    ):
        self.model_name = model_name
        self.stacked_widget_index = stacked_widget_index
        self.setup_from_result_handler = setup_from_result_handler
        self.run_handler = run_handler


result_container: ResultContainer = ResultContainer()


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
            tabledata {
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

    <body style="background-color: white;">
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center; width:100%;">
        """
    html_end = """
    </div>
    </body>
    </html>
    """
    return html_start, html_end


def get_next_valid_result_id():
    if result_container.results:
        return max(result_container.results.keys()) + 1
    else:
        return 0


def select_result(result_id: int):
    if result_id == NO_RESULT_SELECTED:
        result_container.current_result = NO_RESULT_SELECTED
        return
    if result_id in result_container.results.keys():
        result_container.current_result = result_id
        return
    raise ValueError(f"Trying to select non-existing result {result_id}")


def div_title():
    return (
        "<div style=\"font-size:32px;text-align:center; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;">'
    )


def div_text():
    return (
        "<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;">'
    )


def div_table():
    return (
        "<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;overflow:auto;width:100%;">'
    )


def button_y(block, button):
    return 40 + 110 * (button) + 20 * block


def label_y(block, button):
    return 40 + 110 * (button) + 20 * block

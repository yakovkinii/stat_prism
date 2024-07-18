import logging
from typing import TYPE_CHECKING

import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QMimeData, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QDrag
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QMenu, QSizePolicy, QVBoxLayout, QWidget

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method, log_method_noarg
from src.common.size import Font
from src.common.unique_qss import set_stylesheet
from src.core.filter.filter_result import FilterResult
from src.results_panel.results.common.base import BaseResult

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultListItem(QWidget):
    """
    The very item displayed
    """

    def __init__(self, result_id: int, result: BaseResult, parent_widget=None, click_handler=None):
        super().__init__(parent_widget)

        self.result_id: int = result_id
        self.result = result
        self.click_handler = click_handler

        self.layout = QtWidgets.QVBoxLayout(self)
        title_widget = QtWidgets.QLabel(self.result.title)
        context_widget = QtWidgets.QLabel(self.result.title_context + str(self.result.config.filter_id))
        self.layout.addWidget(title_widget)
        self.layout.addWidget(context_widget)

        set_stylesheet(title_widget, "#id{" "color: #000;" "font-family: Segoe UI;" f"font-size: {Font.size}pt;" "}")
        set_stylesheet(
            context_widget, "#id{" "color: #000;" "font-family: Segoe UI;" f"font-size: {Font.size_small}pt;" "}"
        )

    def mousePressEvent(self, event):
        if self.click_handler is not None:
            self.click_handler(self.result_id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        context_menu.addAction(delete_action)

        # Connect the 'delete' action to the slot/function
        # delete_action.triggered.connect(lambda: self.delete_result.emit(self.unique_id))

        # Show the menu at the cursor's current position
        context_menu.exec_(event.globalPos())


class DragDropListWidget(QListWidget):
    """
    Main list widget
    """

    def __init__(self, parent, root_class):
        super().__init__(parent)
        self.top_level_list = self
        self.root_class: MainWindowClass = root_class
        set_stylesheet(
            self,
            "#id{"
            "border: 1px solid #ddd;"
            "outline: 0;"
            "}"
            "#id::item:selected{"
            "background-color: rgb(229,241,251);"
            "border: 1px solid rgb(0,120,215)"
            "}",
        )
        self.setDropIndicatorShown(True)
        self.setObjectName("root")
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)

    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimeData = QMimeData()
        drag.setMimeData(mimeData)
        # Save reference to the widget being dragged
        dragged_item = self.currentItem()
        if dragged_item:
            dragged_widget: ResultListItem = self.itemWidget(dragged_item)
            mimeData.setText(str(dragged_widget.result_id))
            print(f"Dragging {str(dragged_widget.result_id)}")
        drag.exec(supportedActions)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        source_widget = event.source()

        if event.mimeData().hasText():
            result_id = int(event.mimeData().text())
            if (source_widget != self) and isinstance(self.root_class.results_panel.results[result_id], FilterResult):
                event.ignore()
                logging.info("Ignoring drop")
                return
            else:
                logging.info("Accepting drop")

            drop_position = self.indexAt(event.pos()).row()
            if drop_position == -1:  # If dropped outside any item, add to the end
                drop_position = self.count()

            if isinstance(self, DragDropListWidgetItemInner):
                filter_id = self.result_id
                self.root_class.results_panel.results[result_id].config.filter_id = filter_id
            else:
                self.root_class.results_panel.results[result_id].config.filter_id = None

            if isinstance(self.root_class.results_panel.results[result_id], FilterResult):
                # Moving a filter
                item = source_widget.currentItem()
                widget: NestedListContainerWidget = source_widget.itemWidget(item)
                result_ids = []
                for child_item_index in range(widget.inner_list_widget.count()):
                    child_item = widget.inner_list_widget.item(child_item_index)
                    child_widget: ResultListItem = widget.inner_list_widget.itemWidget(child_item)
                    result_ids.append(child_widget.result_id)

                source_item = source_widget.currentItem()
                source_widget.takeItem(source_widget.row(source_item))

                new_filter_widget: NestedListContainerWidget = self.addItemWithCustomWidget(result_id, drop_position)
                for child_id in result_ids:
                    new_filter_widget.inner_list_widget.addItemWithCustomWidget(child_id)
            else:
                source_item = source_widget.currentItem()
                source_widget.takeItem(source_widget.row(source_item))
                self.addItemWithCustomWidget(result_id, drop_position)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

        self.top_level_list.adjust_height()

    def addItemWithCustomWidget(self, result_id, position=None):
        logging.info(f"Adding item with result_id={result_id}, position={position}")
        result = self.root_class.results_panel.results[result_id]

        item = QListWidgetItem()
        if isinstance(result, FilterResult):
            # Creating a FILTER (NESTED LIST)
            widget = NestedListContainerWidget(
                result_id=result_id, result=result, parent=self, root_class=self.root_class
            )
        else:
            widget = ResultListItem(
                result_id=result_id,
                result=result,
            )

        item.setSizeHint(widget.sizeHint())
        if (position is None) or (position < 0) or (position >= self.count()):
            position = self.count()
        self.insertItem(position, item)
        self.setItemWidget(item, widget)
        self.setCurrentRow(position)
        return widget

    def _adjust_height(self):
        # update sizehints of items
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if item is None or widget is None:
                continue
            item.setSizeHint(widget.sizeHint())

    def adjust_height(self):
        logging.info("Adjusting height")
        QTimer.singleShot(50, self._adjust_height)


class DragDropListWidgetItemInner(DragDropListWidget):
    def __init__(self, parent, result_id, root_class, top_level_list):
        super().__init__(parent, root_class)
        self.result_id = result_id
        self.top_level_list = top_level_list
        self.root_class: MainWindowClass = root_class
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(100)
        self.setFixedWidth(200)

    def adjust_height(self):
        height = 0
        for i in range(self.count()):
            height += self.sizeHintForRow(i)
        new_height = height + 2 * self.frameWidth()
        new_height = max(20, new_height)
        print(new_height)
        self.setFixedHeight(new_height)
        return new_height


class NestedListContainerWidget(QWidget):
    def __init__(self, result_id, result, parent, root_class):
        super().__init__(parent)
        self.result_id = result_id
        self.result = result
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.title_widget = QLabel(result.title)
        self.layout.addWidget(self.title_widget)
        set_stylesheet(
            self.title_widget, "#id{" "color: #000;" "font-family: Segoe UI;" f"font-size: {Font.size}pt;" "}"
        )

        self.inner_list_widget = DragDropListWidgetItemInner(self, result_id, root_class, parent)
        self.layout.addWidget(self.inner_list_widget)

    def adjust_height(self):
        self.inner_list_widget.adjust_height()

    def sizeHint(self):
        self.inner_list_widget.adjust_height()
        return self.layout.sizeHint()


class ResultSelectorClass:
    def __init__(self, parent_widget, parent_class, root_class):
        """
        list of results is drawn here in order.
        The items are identified by result id.

        """
        # Setup
        self._width = 220
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setFixedWidth(self._width)

        self.widget_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 5, 0)

        button = QtWidgets.QPushButton("Add Study")
        button.clicked.connect(self.add_result_handler)
        # font size
        set_stylesheet(
            button,
            "#id{"
            "background-color: #fff;"
            "font-family: Segoe UI;"
            f"font-size: {Font.size}pt;"
            "border: 1px solid #ddd;"
            "}"
            "#id:hover{"
            "background-color: rgb(229,241,251);"
            "border: 1px solid rgb(0,120,215)"
            "}",
        )
        icon = qta.icon("fa5s.plus")
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        button.setFixedHeight(60)

        self.widget_layout.addWidget(button)

        self.list_widget = DragDropListWidget(self.widget, root_class)

        # self.list_widget.setFixedWidth(self._width)
        self.widget_layout.addWidget(self.list_widget)
        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        # self.widget.addItem("Result1")
        # self.widget.addItem("Result2")

    @log_method_noarg
    def add_all_results(self):
        for result in self.root_class.results_panel.results.values():
            self.add_result(result)

    @log_method
    def add_result(self, result: BaseResult):
        self.list_widget.addItemWithCustomWidget(result.unique_id)

    @log_method
    def add_result_handler(self, *args, **kwargs):
        logging.info("Trying to add result")
        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.select_study_panel_index)

    @log_method
    def activate_result_handler(self, unique_id):
        logging.info(f"Trying to activate result with unique_id: {unique_id}")
        result = self.root_class.results_panel.results[unique_id]

        self.root_class.settings_panel.panels[result.settings_panel_index].configure(result=result)
        self.root_class.action_activate_panel_by_index(result.settings_panel_index)
        self.root_class.results_panel.result_display.configure(self.root_class.results_panel.results[unique_id])

    @log_method
    def delete_result_handler(self, unique_id):
        logging.info(f"Trying to delete result with unique_id: {unique_id}")
        result_index = self.list_widget.currentRow()
        self.list_widget.takeItem(result_index)
        self.root_class.results_panel.results.pop(unique_id)
        if self.root_class.results_panel.results:
            self.activate_result_handler(list(self.root_class.results_panel.results.keys())[0])
            self.list_widget.setCurrentRow(0)

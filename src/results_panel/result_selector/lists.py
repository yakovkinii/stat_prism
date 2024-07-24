import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QMimeData, Qt, QTimer
from PySide6.QtGui import QAction, QDrag
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QMenu, QSizePolicy, QVBoxLayout, QWidget

from src.common.size import Font
from src.common.unique_qss import set_stylesheet
from src.core.filter.filter_result import FilterResult
from src.results_panel.result_selector.result_item import ResultListItem

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class DragDropListWidget(QListWidget):
    """
    Main list widget
    """

    def __init__(self, parent, root_class, click_handler, delete_handler):
        super().__init__(parent)
        self.click_handler = click_handler
        self.delete_handler = delete_handler
        self.top_level_list = self
        self.root_class: MainWindowClass = root_class
        self.setDropIndicatorShown(False)
        self.setObjectName("root")
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSpacing(2)

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

            if source_widget != self:
                self.root_class.results_panel.results[result_id].needs_update = True

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

            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            source_widget.clearSelection()
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
                result_id=result_id,
                result=result,
                parent=self,
                root_class=self.root_class,
                click_handler=self.click_handler,
                delete_handler=self.delete_handler,
            )
        else:
            widget = ResultListItem(
                result_id=result_id,
                result=result,
                parent_widget=self,
                click_handler=self.click_handler,
                delete_handler=self.delete_handler,
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
    def __init__(self, parent, result_id, root_class, top_level_list, click_handler, delete_handler):
        self.click_handler = click_handler
        self.delete_handler = delete_handler

        super().__init__(parent, root_class, click_handler, delete_handler)
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
    def __init__(self, result_id, result, parent, root_class, click_handler, delete_handler):
        super().__init__(parent)
        self.click_handler = click_handler
        self.delete_handler = delete_handler

        self.result_id = result_id
        self.result = result
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

        if result.config.query:
            self.title_widget = QLabel(result.config.query)
        else:
            self.title_widget = QLabel("Filter")

        self.layout.addWidget(self.title_widget)
        set_stylesheet(
            self.title_widget, "#id{" "color: #000;" "font-family: Segoe UI;" f"font-size: {Font.size_small}pt;" "}"
        )

        self.inner_list_widget = DragDropListWidgetItemInner(
            self, result_id, root_class, parent, click_handler, delete_handler
        )
        self.layout.addWidget(self.inner_list_widget)

    def adjust_height(self):
        self.inner_list_widget.adjust_height()

    def sizeHint(self):
        self.inner_list_widget.adjust_height()
        return self.layout.sizeHint()

    def mousePressEvent(self, event):
        if self.click_handler is not None:
            self.click_handler(self.result_id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        context_menu.addAction(delete_action)

        # Connect the 'delete' action to the slot/function
        delete_action.triggered.connect(self.delete_handler)

        # Show the menu at the cursor's current position
        context_menu.exec_(event.globalPos())

    def refresh(self):
        if self.result.config.query:
            self.title_widget.setText(self.result.config.query)
        else:
            self.title_widget.setText("Filter")

        for i in range(self.inner_list_widget.count()):
            item = self.inner_list_widget.item(i)
            widget = self.inner_list_widget.itemWidget(item)
            widget.refresh()

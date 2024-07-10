import logging

from PyQt5.QtCore import  Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QListWidget,
    QTextEdit,
)

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet


class EditableLabel(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        set_stylesheet(self, "#id{border: none; background-color: rgba(255,255,255,100);}")
        if DEBUG_LAYOUT:
            set_stylesheet(self, "#id{border: 1px solid blue; background-color: #eef;}")

        self.setCursorPosition(0)
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        self.setCursorPosition(0)
        self.clearFocus()


class EditableLabelWordwrap(QTextEdit):
    editingFinished = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(388)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        set_stylesheet(self, "#id{border: none; background-color: rgba(255,255,255,100);}")
        if DEBUG_LAYOUT:
            set_stylesheet(self, "#id{border: 1px solid blue; background-color: #eef;}")
        self.textChanged.connect(self.adjustHeightToFitText)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.accept_editing = True

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.clearFocus()  # will emit editingFinished
                return True

            if event.key() == Qt.Key_Escape:
                self.accept_editing = False
                self.clearFocus()
                return True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        self.accept_editing = True
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.editingFinished.emit(self.accept_editing)
        super().focusOutEvent(event)

    def text(self):
        return self.toPlainText()

    def adjustHeightToFitText(self):
        doc = self.document()
        doc.setTextWidth(388.0)
        self.setFixedHeight(doc.size().height() + 2 * self.frameWidth())

    def scheduleAdjustHeightToFitText(self):
        QTimer.singleShot(10, self.adjustHeightToFitText)


class CheckListWidget(QListWidget):
    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        # never display horizontal scrollbar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # vertical scrollbar width of 10px
        set_stylesheet(
            self,
            """
            #id {border: 1px solid #ddd;}
            #id::item {
                color: #333; 
                background-color: #fff;
                padding: 2px;
                border-bottom: 1px solid #eee;
            }
            #id::indicator {
                margin-top: 2px;
                width: 20px;  /* Makes the checkbox appear larger */
                height: 20px;
            }
            #id::indicator:checked {
                image: url(:/mat/resources/checked.png);
            }
            
            #id::indicator:unchecked {
                image: url(:/mat/resources/unchecked.png);
            }
            
            #id::indicator:checked:disabled {
                image: url(:/mat/resources/checked_disabled.png);
            }
            
            #id::indicator:unchecked:disabled {
                image: url(:/mat/resources/unchecked_disabled.png);
            }
            """,
        )
        self.setMouseTracking(True)
        self._fillingState = None
        self.start_item = None
        self.start_item_check_state = None

    def add_item_custom(self, item, checkable=True, checked=False, widget=None):
        if checkable:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        else:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        self.addItem(item)
        if widget is not None:
            self.setItemWidget(item, widget)

    def mousePressEvent(self, event):
        # super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            button = event.button()
            if button == Qt.LeftButton:
                self._fillingState = Qt.Checked
            elif button == Qt.RightButton:
                self._fillingState = Qt.Unchecked
            else:
                return
            self.start_item = item
            self.start_item_check_state = item.checkState()
            self.toggleCheckState(item)

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        # super().mouseReleaseEvent(event)

        if item == self.start_item and (item.flags() & Qt.ItemIsEnabled) and (event.button() == Qt.LeftButton):
            item.setCheckState(Qt.Checked if self.start_item_check_state == Qt.Unchecked else Qt.Unchecked)

        self._fillingState = None
        self.selection_changed.emit()

    def mouseMoveEvent(self, event):
        if self._fillingState is not None:
            item = self.itemAt(event.pos())
            if item:
                self.toggleCheckState(item)
        # super().mouseMoveEvent(event)

    def toggleCheckState(self, item):
        if self._fillingState is None:
            return
        if item.flags() & Qt.ItemIsEnabled:
            item.setCheckState(self._fillingState)

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QTextEdit

from src.common.constant import DEBUG_LAYOUT
from src.common.size import SettingsPanelSize
from src.common.unique_qss import set_stylesheet


class EditableLabelWordwrap(QTextEdit):
    editingFinished = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(SettingsPanelSize.width - 15)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        set_stylesheet(self, "#id{border: none; background-color: rgba(255,255,255,100);}")
        if DEBUG_LAYOUT:
            set_stylesheet(self, "#id{border: 1px solid blue; background-color: #eef;}")
        self.textChanged.connect(self.adjustHeightToFitText)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.accept_editing = True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.clearFocus()  # will emit editingFinished
                return True

            if event.key() == Qt.Key.Key_Escape:
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
        self.setFixedHeight(int(doc.size().height() + 2 * self.frameWidth()))

    def scheduleAdjustHeightToFitText(self):
        QTimer.singleShot(10, self.adjustHeightToFitText)


class CheckListWidget(QListWidget):
    selection_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        # never display horizontal scrollbar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
                width: 18px;  /* Makes the checkbox appear larger */
                height: 18px;
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
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        else:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.addItem(item)
        if widget is not None:
            self.setItemWidget(item, widget)

    def mousePressEvent(self, event):
        # super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            button = event.button()
            if button == Qt.MouseButton.LeftButton:
                self._fillingState = Qt.CheckState.Checked
            elif button == Qt.MouseButton.RightButton:
                self._fillingState = Qt.CheckState.Unchecked
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

        if (
            item == self.start_item
            and (item.flags() & Qt.ItemFlag.ItemIsEnabled)
            and (event.button() == Qt.MouseButton.LeftButton)
        ):
            item.setCheckState(
                Qt.CheckState.Checked
                if self.start_item_check_state == Qt.CheckState.Unchecked
                else Qt.CheckState.Unchecked
            )

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
        if item.flags() & Qt.ItemFlag.ItemIsEnabled:
            item.setCheckState(self._fillingState)

from PyQt5.QtCore import QRect, QSize
from PyQt5.QtWidgets import QLayout, QWidgetItem


class VerticalLayout(QLayout):
    def __init__(self, parent, padding_left=0, padding_right=0, padding_top=0, padding_bottom=0, spacing=0, top_level=False):
        super().__init__(parent)
        self.parent=parent
        self.top_level=top_level
        self.padding_left=padding_left
        self.padding_right=padding_right
        self.padding_top=padding_top
        self.padding_bottom=padding_bottom
        self.spacing=spacing
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
            widget_height = item.sizeHint().height()
            item.setGeometry(QRect(x, y, rect.width()-self.padding_left-self.padding_right,
                                   widget_height))
            y += widget_height + self.spacing

    def sizeHint(self):
        if self.top_level:
            return self.parent.size()
        height = self.padding_top+self.padding_bottom+self.spacing*(len(self.items)-1)
        height += sum(item.sizeHint().height() for item in self.items)
        width = max(item.sizeHint().width() for item in self.items) + self.padding_left+self.padding_right
        return QSize(width, height)

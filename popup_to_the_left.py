#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QFrame, QLabel
)
from PySide6.QtCore import QPoint, Qt
import sys

class FloatingPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Extra settings"))
        self.setFixedWidth(180)
        self.setFixedHeight(140)  # <-- fixed-ish height
        self.setStyleSheet("background: white;")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout(self)

        self.main_area = QLabel("Main screen")
        self.main_area.setStyleSheet("background:#ddd;")
        main_layout.addWidget(self.main_area, 1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        sidebar_content = QWidget()
        v = QVBoxLayout(sidebar_content)

        self.items = []
        for i in range(20):
            btn = QPushButton(f"Item {i}")
            btn.clicked.connect(lambda _, b=btn: self.show_panel_for(b))
            v.addWidget(btn)
            self.items.append(btn)
        v.addStretch()
        self.scroll.setWidget(sidebar_content)
        main_layout.addWidget(self.scroll)

        self.panel = FloatingPanel(self)
        self.panel.hide()

        self.scroll.verticalScrollBar().valueChanged.connect(self.reposition_panel)

        self.current_item = None

    def show_panel_for(self, item_widget):
        self.current_item = item_widget
        self.panel.show()
        self.reposition_panel()

    def reposition_panel(self):
        if not self.current_item or not self.panel.isVisible():
            return

        item_pos_in_self = self.current_item.mapTo(self, QPoint(0, 0))
        sidebar_pos_in_self = self.scroll.mapTo(self, QPoint(0, 0))

        gap = -10
        x = sidebar_pos_in_self.x() - self.panel.width() - gap

        # --- center panel on the item vertically ---
        item_h = self.current_item.height()
        panel_h = self.panel.height()
        y = item_pos_in_self.y() + (item_h // 2) - (panel_h // 2)

        # clamp so it doesn't go off top/bottom of main widget
        y = max(0, min(y, self.height() - panel_h - 5))

        self.panel.move(x, y)
        self.panel.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(800, 500)
    w.show()
    sys.exit(app.exec())


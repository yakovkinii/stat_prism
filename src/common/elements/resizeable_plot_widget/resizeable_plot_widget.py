import pyqtgraph as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QCursor, QGuiApplication, QImage, QPainter
from PySide6.QtWidgets import QApplication, QMenu


class ResizablePlotWidget(pg.PlotWidget):
    def __init__(self, parent_widget, result_element):
        super().__init__(parent_widget)
        pg.setConfigOptions(antialias=True)
        self.result_element = result_element
        self.setMouseTracking(True)  # Enable mouse tracking to update the cursor dynamically
        self.dragging = False
        self.resizeDirection = None
        self.edge_threshold = 10  # Sensitivity range for cursor change near the edges

    def mouseMoveEvent(self, event):
        x, y = event.position().x(), event.position().y()
        width, height = self.width(), self.height()

        if width - x <= self.edge_threshold and height - y <= self.edge_threshold:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif width - x <= self.edge_threshold:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif height - y <= self.edge_threshold:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        else:
            self.unsetCursor()

        if self.dragging:
            if self.resizeDirection == "horizontal":
                self.resize(max(x, 100), height)
                self.result_element.general_plot_config.size_x = max(x, 100)
            elif self.resizeDirection == "vertical":
                self.resize(width, max(y, 100))
                self.result_element.general_plot_config.size_y = max(y, 100)
            elif self.resizeDirection == "both":
                self.resize(max(x, 100), max(y, 100))
                self.result_element.general_plot_config.size_x = max(x, 100)
                self.result_element.general_plot_config.size_y = max(y, 100)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        x, y = event.position().x(), event.position().y()
        width, height = self.width(), self.height()

        if event.button() == Qt.LeftButton:
            if width - x <= self.edge_threshold and height - y <= self.edge_threshold:
                self.dragging = True
                self.resizeDirection = "both"
                event.accept()
                return

            elif width - x <= self.edge_threshold:
                self.dragging = True
                self.resizeDirection = "horizontal"
                event.accept()
                return
            elif height - y <= self.edge_threshold:
                self.dragging = True
                self.resizeDirection = "vertical"
                event.accept()
                return
            super().mousePressEvent(event)

        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.resizeDirection = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_as_image_to_clipboard)
        context_menu.addAction(copy_action)
        context_menu.exec(event.globalPos())
        event.accept()

    def copy_as_image_to_clipboard(self):
        # Set a more reasonable DPI for better image quality
        dpi = 96
        logical_dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
        size = QSize(self.width() * dpi / logical_dpi, self.height() * dpi / logical_dpi)
        image = QImage(size, QImage.Format_ARGB32)
        image.setDevicePixelRatio(dpi / 96.0)  # 96 DPI is the default DPI

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing
        self.render(painter)
        painter.end()

        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

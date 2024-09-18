import base64
import os

import pyqtgraph as pg
import pyqtgraph.exporters
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCursor, QImage
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
        exporter = pg.exporters.ImageExporter(self.getPlotItem())
        exporter.parameters()["width"] = 1280  # (note this also affects height parameter)
        temp_file_name = "./~tmp.png"
        exporter.export(temp_file_name)

        image = QImage()
        image.load(temp_file_name)

        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

        os.remove(temp_file_name)

    def render_to_html(self):
        exporter = pg.exporters.ImageExporter(self.getPlotItem())
        exporter.parameters()["width"] = 600  # (note this also affects height parameter)
        temp_file_name = "./~tmp.png"
        exporter.export(temp_file_name)

        with open(temp_file_name, "rb") as f:
            image = f.read()
            base64_encoded_image = f"data:image/bmp;base64,{base64.b64encode(image).decode('utf-8')}"

        html = f'<img src="{base64_encoded_image}" alt="Plot Image" style="width: 400px; height: auto;">'
        os.remove(temp_file_name)
        return html

#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser,
    QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import QSize, Qt


class AnalysisOutputWidget(QWidget):
    def __init__(self, parent=None, html=""):
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Add header label
        header_label = QLabel("Analysis Output")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(header_label)

        # Add APA-style table
        self.text_browser = AutoSizingTextBrowser()
        self.text_browser.setHtml(html)
        self.text_browser.setFrameStyle(0)
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setStyleSheet("""
            background: white; 
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        """)
        layout.addWidget(self.text_browser)

        # Add a button under the table
        self.button = QPushButton("Continue")
        self.button.setFixedWidth(120)
        layout.addWidget(self.button, 0, Qt.AlignCenter)


class AutoSizingTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def sizeHint(self) -> QSize:
        # Calculate the document size
        doc = self.document()
        doc.setTextWidth(self.viewport().width())

        # Get margins and padding
        margins = self.contentsMargins()
        padding = 24  # Matches our CSS padding

        # Calculate total required size
        width = doc.idealWidth() + margins.left() + margins.right() + padding
        height = doc.size().height() + margins.top() + margins.bottom() + padding

        return QSize(int(width), int(height))

    def resizeEvent(self, event):
        self.updateGeometry()  # Ensure size hint is recalculated when width changes
        super().resizeEvent(event)


html_content = """
<div style="font-family: 'Times New Roman'; font-size: 12pt; line-height: 1.8;">
  <!-- Your HTML content here -->
</div>
"""

output_widget = AnalysisOutputWidget(parent=None, html=html_content)

# Example usage
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    output_widget.show()
    sys.exit(app.exec())
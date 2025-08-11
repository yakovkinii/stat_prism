from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTextBrowser,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
)


class AutoSizingTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            """
            background: white; 
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        """
        )

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

    def set_html(self, html: str):
        super().setHtml(html)
        self.updateGeometry()


html = """
<div class="double-spacing font"><b>
            Table 
            </b></div>
        <div class="double-spacing font"><i>(Table caption)</i></div><br><table style="border-top: 2px solid black;border-bottom: 2px solid black;" class="font"></table>
<br><br>
<div class="double-spacing font"> 
<div style="font-size: 10pt"><b>Please configure the analysis using the panel on the right</b></div><div style="">
<h2> Descriptive Statistics</h2>
<h3> Description </h3>
<div>
    Generate summary statistics for the selected variable(s) and grouping column (if any).
</div>
<h3> Inputs </h3>
<div>
    <b>Variable(s):</b><br>
    The variable(s) to describe.
</div>
<div>
    <b>Grouping Column:</b><br>
    The column that defines the groups to compare (such as respondent's sex or age group).
</div>
</div>
</div><br>


            <div class="double-spacing font"><b>
            Table 
            </b></div>
        <div class="double-spacing font"><i>Descriptive statistics</i></div><br><table style="border-top: 2px solid black;border-bottom: 2px solid black;" class="font"><tr><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;"  colspan="2">Shapiro-Wilk</td></tr><tr><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" ></td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >N</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Missing</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Mean</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >SD</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Min</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Max</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >W</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >p</td></tr><tr><td style="padding: 5px;width: 80px;text-align: left; padding-left: 0px; margin-left:0px;" >Age</td><td style="padding: 5px;width: 80px;text-align: center;" >10</td><td style="padding: 5px;width: 80px;text-align: center;" >0</td><td style="padding: 5px;width: 80px;text-align: center;" >54.6</td><td style="padding: 5px;width: 80px;text-align: center;" >26.99</td><td style="padding: 5px;width: 80px;text-align: center;" >12</td><td style="padding: 5px;width: 80px;text-align: center;" >90</td><td style="padding: 5px;width: 80px;text-align: center;" >.954</td><td style="padding: 5px;width: 80px;text-align: center;" >.720</td></tr><tr><td style="padding: 5px;width: 80px;text-align: left; padding-left: 0px; margin-left:0px;" >Height</td><td style="padding: 5px;width: 80px;text-align: center;" >10</td><td style="padding: 5px;width: 80px;text-align: center;" >0</td><td style="padding: 5px;width: 80px;text-align: center;" >149.5</td><td style="padding: 5px;width: 80px;text-align: center;" >34.52</td><td style="padding: 5px;width: 80px;text-align: center;" >102</td><td style="padding: 5px;width: 80px;text-align: center;" >194</td><td style="padding: 5px;width: 80px;text-align: center;" >.917</td><td style="padding: 5px;width: 80px;text-align: center;" >.334</td></tr></table>


            <div class="double-spacing font"><b>
            Table 
            </b></div>
        <div class="double-spacing font"><i>Descriptive statistics</i></div><br><table style="border-top: 2px solid black;border-bottom: 2px solid black;" class="font"><tr><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;text-align: center;" ></td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;"  colspan="2">Shapiro-Wilk</td></tr><tr><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" ></td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >N</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Missing</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Mean</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >SD</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Min</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >Max</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >W</td><td style="padding: 5px;width: 80px;border-bottom: 1px solid black;text-align: center;" >p</td></tr><tr><td style="padding: 5px;width: 80px;text-align: left; padding-left: 0px; margin-left:0px;" >Age</td><td style="padding: 5px;width: 80px;text-align: center;" >10</td><td style="padding: 5px;width: 80px;text-align: center;" >0</td><td style="padding: 5px;width: 80px;text-align: center;" >54.6</td><td style="padding: 5px;width: 80px;text-align: center;" >26.99</td><td style="padding: 5px;width: 80px;text-align: center;" >12</td><td style="padding: 5px;width: 80px;text-align: center;" >90</td><td style="padding: 5px;width: 80px;text-align: center;" >.954</td><td style="padding: 5px;width: 80px;text-align: center;" >.720</td></tr><tr><td style="padding: 5px;width: 80px;text-align: left; padding-left: 0px; margin-left:0px;" >Height</td><td style="padding: 5px;width: 80px;text-align: center;" >10</td><td style="padding: 5px;width: 80px;text-align: center;" >0</td><td style="padding: 5px;width: 80px;text-align: center;" >149.5</td><td style="padding: 5px;width: 80px;text-align: center;" >34.52</td><td style="padding: 5px;width: 80px;text-align: center;" >102</td><td style="padding: 5px;width: 80px;text-align: center;" >194</td><td style="padding: 5px;width: 80px;text-align: center;" >.917</td><td style="padding: 5px;width: 80px;text-align: center;" >.334</td></tr></table>
"""

app = QApplication([])

# Main container widget
main_widget = QWidget()
main_layout = QVBoxLayout(main_widget)
main_layout.setContentsMargins(12, 12, 12, 12)
main_layout.setSpacing(12)

# Add a header label
header_label = QLabel("Analysis Output")
header_label.setAlignment(Qt.AlignCenter)
header_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
main_layout.addWidget(header_label)

# Add APA-style table
text_browser = AutoSizingTextBrowser()
text_browser.set_html(html)
main_layout.addWidget(text_browser)

# Add a button under the table
button = QPushButton("Continue")
button.setFixedWidth(120)
main_layout.addWidget(button, 0, Qt.AlignCenter)

# Don't add stretch - we want the content to determine the minimum size

# Wrap the entire thing in a scroll area
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(main_widget)
scroll_area.setStyleSheet("border: none;")

# Top-level window
window = QWidget()
window_layout = QVBoxLayout(window)
window_layout.setContentsMargins(0, 0, 0, 0)
window_layout.addWidget(scroll_area)

window.resize(600, 400)
window.setWindowTitle("Analysis Results")
window.show()
app.exec()

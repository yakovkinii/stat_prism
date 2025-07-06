from PySide6 import QtWidgets, QtGui, QtCore


class CustomColorDialog(QtWidgets.QDialog):
    """
    A custom color picker dialog with a 4x7 grid of colors and an alpha slider.
    Rows: raw, lighter, base, darker.
    Usage:
        color = CustomColorDialog.getColor(initial=QtGui.QColor(255,255,255), parent=None)
        if color.isValid():
            r, g, b, a = color.getRgb()
    """

    def __init__(self, initial: QtGui.QColor = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Color")
        self.selected_color = QtGui.QColor(initial or QtGui.QColor(255, 255, 255))
        self.selected_btn = None

        # Original 7 base hues
        base_colors = [
            (100, 100, 255),
            (255, 100, 100),
            (100, 200, 100),
            (255, 100, 0),
            (200, 100, 200),
            (100, 200, 200),
            (100, 100, 100),
        ]

        main_layout = QtWidgets.QVBoxLayout(self)

        # Grid of color buttons (4 rows x 7 cols)
        grid_widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout(grid_widget)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        for row in range(4):
            for col, (r, g, b) in enumerate(base_colors):
                # determine RGB variant per row
                if row == 0:
                    # raw: original
                    pr = 255 if r > 120 else 0
                    pg = 255 if g > 120 else 0
                    pb = 255 if b > 120 else 0
                    if (r, g, b) == (255, 100, 0):
                        pr, pg, pb = (255, 128, 0)

                elif row == 1:
                    # lighter: mix with white 50%
                    pr = int(r + (255 - r) * 0.5)
                    pg = int(g + (255 - g) * 0.5)
                    pb = int(b + (255 - b) * 0.5)
                elif row == 2:
                    # base: original (repeat raw)
                    pr, pg, pb = r, g, b
                else:
                    # darker: mix with black 40%
                    pr = int(r * 0.6)
                    pg = int(g * 0.6)
                    pb = int(b * 0.6)

                color = QtGui.QColor(pr, pg, pb)
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(40, 40)
                btn.setStyleSheet(f"background-color: rgb({pr},{pg},{pb}); border: 1px solid #eee;")
                btn.clicked.connect(lambda _, b=btn, c=color: self._on_color_selected(b, c))
                grid_layout.addWidget(btn, row, col)

        main_layout.addWidget(grid_widget)

        # Alpha slider
        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(QtWidgets.QLabel("Alpha:"))
        self.alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.alpha_slider.setRange(0, 255//5)
        self.alpha_slider.setValue(self.selected_color.alpha())
        self.alpha_slider.valueChanged.connect(self._on_alpha_changed)
        slider_layout.addWidget(self.alpha_slider)
        main_layout.addLayout(slider_layout)

        # OK / Cancel buttons
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box)

    def _on_color_selected(self, btn: QtWidgets.QPushButton, color: QtGui.QColor):
        # reset previous button border
        if self.selected_btn:
            prev_style = self.selected_btn.styleSheet()
            restored = prev_style.replace("border: 2px solid #aaa;", "border: 1px solid #eee;")
            self.selected_btn.setStyleSheet(restored)
        # highlight current button with outer light border
        btn_style = btn.styleSheet().replace("border: 1px solid #eee;", "border: 2px solid #aaa;")
        btn.setStyleSheet(btn_style)
        self.selected_btn = btn

        # update selected color, preserving alpha
        color.setAlpha(self.alpha_slider.value())
        self.selected_color = color

    def _on_alpha_changed(self, value: int):
        self.selected_color.setAlpha(value*5)

    @staticmethod
    def getColor(initial: QtGui.QColor = None, parent=None) -> QtGui.QColor:
        dlg = CustomColorDialog(initial, parent)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            return dlg.selected_color
        return QtGui.QColor()  # invalid


# Example standalone run
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    color = CustomColorDialog.getColor(initial=QtGui.QColor(100, 200, 100))
    if color.isValid():
        print("Selected RGBA:", color.getRgb())
    else:
        print("No color selected.")

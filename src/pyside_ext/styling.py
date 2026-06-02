#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

from PySide6 import QtGui

_font_regular = QtGui.QFont("Segoe UI")
_font_regular.setPointSize(12)

_font_result_label = QtGui.QFont("Segoe UI")
_font_result_label.setPointSize(16)

_font_result_element_label = QtGui.QFont("Segoe UI")
_font_result_element_label.setPointSize(10)


class Style:
    font_regular = _font_regular
    font_result_label = _font_result_label
    font_result_element_label = _font_result_element_label

    class Color(Enum):
        def __str__(self):
            return str(self.value)

        BackgroundElevated = "#eee"
        BackgroundEdit = "#fff"
        Background = "#fff"
        BackgroundNotSelected = "#f5f5f5"
        BackgroundPanel = "#f0f0f0"  # For panel backgrounds
        BorderElevated = "#ccc"
        Border = "#eee"
        Highlight = "#05f"
        Danger = "#700"
        Text = "#000"
        SimpleToolButton = "#888"
        SecondaryText = "#666"  # For secondary/helper text

    class FontFamily(Enum):
        def __str__(self):
            return str(self.value)

        SegoeUI = "Segoe UI"

    class FontSize(Enum):
        def __str__(self):
            return str(self.value)

        smallest = "9pt"
        smaller = "10pt"
        small = "11pt"
        regular = "12pt"
        larger = "14pt"

    class General(Enum):
        def __str__(self):
            return str(self.value)

        # Border styles
        border_standard = "1px solid"
        border_secondary = "2px solid"  # For secondary elements like blocks
        border_thick = "5px solid"  # For major UI elements

        # Complete borders
        border = "1px solid #eee"  # Standard border
        border_elevated = "1px solid #ccc"  # For elevated elements
        border_secondary_text = "2px solid #666"  # For secondary UI elements
        border_highlight = "2px solid #05f"  # For highlighted elements

        # Legacy borders (to be deprecated)
        border_data_analysis = "5px solid #aaf"  # Todo deprecate
        border_thick_unselected = "5px solid #eee"
        border_thick_selected = "5px solid #05f"
        border_thin_unselected = "2px solid #eee"
        border_thin_selected = "2px solid #05f"

        # Spacing
        padding_tiny = "2px"
        padding_small = "4px"
        padding_medium = "8px"
        padding_large = "16px"
        padding_xlarge = "32px"

        margin_tiny = "2px"
        margin_small = "4px"
        margin_medium = "8px"
        margin_large = "16px"
        margin_xlarge = "32px"

        # Element dimensions with paired values (px string for CSS, int for Qt)
        scrollbar_width_css = "15px"
        scrollbar_width = 15

        checkbox_size_css = "16px"
        checkbox_size = 16

        main_tab_width_css = "40px"
        main_tab_width = 40

        # Standard heights
        button_height_small_css = "50px"
        button_height_small = 50

        button_height_large_css = "70px"
        button_height_large = 70

        navigation_height_css = "80px"
        navigation_height = 80

        study_height_css = "80px"
        study_height = 80

        # Standard widths
        color_button_size_css = "35px"
        color_button_size = 35

        icon_button_size_css = "32px"
        icon_button_size = 32

        spinbox_width_css = "100px"
        spinbox_width = 100

        flip_label_width_css = "32px"
        flip_label_width = 32

        min_edit_width_css = "200px"
        min_edit_width = 200

        # Spacer heights
        spacer_small_css = "8px"
        spacer_small = 8

        spacer_medium_css = "20px"
        spacer_medium = 20

        spacer_large_css = "40px"
        spacer_large = 40

        # Border radiuses
        border_radius_small = "4px"
        border_radius_medium = "5px"
        border_radius_large = "8px"

        # Content padding
        content_padding_small = "8px"
        content_padding_medium = "12px"
        content_padding_large = "16px"

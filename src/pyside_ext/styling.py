#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

from PySide6 import QtGui

from src.common.ui_theme import ACTIVE_THEME as _ACTIVE_THEME

_font_regular = QtGui.QFont("Segoe UI")
_font_regular.setPointSize(12)

_font_result_label = QtGui.QFont("Segoe UI")
_font_result_label.setPointSize(16)

# Smaller, bold study title shown in the main area (brand-coloured).
_font_study_title = QtGui.QFont("Segoe UI")
_font_study_title.setPointSize(12)
_font_study_title.setBold(True)

_font_result_element_label = QtGui.QFont("Segoe UI")
_font_result_element_label.setPointSize(10)


class Scheme:
    """Active UI colour scheme — the single source of truth for widget colours.

    Its attributes are populated from the active palette in ``src/common/ui_theme.py``
    (LIGHT or DARK). ``Style.Color`` / ``Style.General`` reference these names, and every
    widget references ``Style.Color``, so colours are not hardcoded anywhere else.

    To switch the whole UI light/dark, change ``ACTIVE_THEME`` in ``src/common/ui_theme.py``
    (takes effect on the next start).
    """


for _key, _value in _ACTIVE_THEME.items():
    setattr(Scheme, _key, _value)


class Style:
    font_regular = _font_regular
    font_result_label = _font_result_label
    font_result_element_label = _font_result_element_label
    font_study_title = _font_study_title

    class Color(Enum):
        def __str__(self):
            return str(self.value)

        # Semantic tokens — every value references Scheme (the single colour source above).
        # Widgets use these tokens; never hardcode a colour in a widget.
        BackgroundElevated = Scheme.surface_elevated
        BackgroundEdit = Scheme.surface_edit
        Background = Scheme.surface_main
        BackgroundNotSelected = Scheme.surface_not_selected
        BackgroundPanel = Scheme.surface_panel
        BorderElevated = Scheme.border_elevated
        Border = Scheme.border
        Highlight = Scheme.accent
        Selection = Scheme.selection
        Danger = Scheme.danger
        Text = Scheme.text
        SimpleToolButton = Scheme.tool_glyph
        SecondaryText = Scheme.text_secondary
        # Tokens for things that used to be hardcoded inside individual widgets:
        Overlay = Scheme.overlay
        TableRule = Scheme.table_rule
        ToggleOn = Scheme.toggle_on
        ToggleOff = Scheme.toggle_off
        TextOnLight = Scheme.text_on_light
        TypeNumeric = Scheme.type_numeric
        TypeNominal = Scheme.type_nominal
        TypeOrdinal = Scheme.type_ordinal
        TypeId = Scheme.type_id
        TitleBrand = Scheme.title_brand

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

        # Complete borders (colours reference Scheme)
        border = f"1px solid {Scheme.border}"  # Standard border
        border_elevated = f"1px solid {Scheme.border_elevated}"  # For elevated elements
        border_secondary_text = f"2px solid {Scheme.text_secondary}"  # For secondary UI elements
        border_highlight = f"2px solid {Scheme.accent}"  # For highlighted elements

        # Thick/thin selected-vs-unselected borders (result cards, raw-data rows).
        border_thick_unselected = f"5px solid {Scheme.border}"
        border_thick_selected = f"5px solid {Scheme.accent}"
        border_thin_unselected = f"2px solid {Scheme.border}"
        border_thin_selected = f"2px solid {Scheme.accent}"
        border_thin_selected_element = f"2px solid {Scheme.text_secondary}"

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

#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

from PySide6 import QtGui

_font_regular = QtGui.QFont("Segoe UI")
_font_regular.setPointSize(12)

_font_result_label = QtGui.QFont("Segoe UI")
_font_result_label.setPointSize(16)

_font_result_element_label = QtGui.QFont("Segoe UI")
_font_result_element_label.setPointSize(10)


class Scheme:
    """Single source of truth for the UI colour scheme — **change colours here.**

    Brand palette (deep navy / pale gold / cream) plus a few derived accents. ``Style.Color``
    and ``Style.General`` reference these names, and every widget references ``Style.Color`` —
    so colours are not hardcoded anywhere else. (To add a light theme later, swap these values
    or make this class selectable at runtime.)
    """

    # Two-tone: the chrome (right settings panel, menus, buttons) is the banner navy blue; the
    # main area it contrasts against is near-black.
    surface_panel = "#0d1b2a"          # banner navy — right settings panel
    surface_main = "#070809"           # near-black — main area + result surfaces (the contrast)
    surface_edit = "#0a1623"           # input fields (slightly deeper navy than the panel)
    surface_not_selected = "#12283c"
    surface_elevated = "#14293e"       # menus, buttons, popups, table headers (lifted navy)

    # Borders (navy, to sit on the navy chrome)
    border = "#26405c"
    border_elevated = "#345578"

    # Text / glyphs
    text = "#e8e6da"                   # primary cream/light
    text_secondary = "#9a9a93"         # muted helper text (neutral, not blue)
    text_on_light = "#15233b"          # text drawn on a light pastel column tag
    tool_glyph = "#a6a6a0"             # simple tool-button icons

    # Accents
    accent = "#e6c860"                 # brand gold — highlights / selection borders
    accent_blue = "#3a5a8c"            # legacy data-analysis accent
    selection = "#3a3320"              # selected-row background — dark warm gold tint, not blue
    danger = "#ff6b6b"

    # Misc UI bits
    overlay = "rgba(0,0,0,0.55)"       # dimmed modal background
    table_rule = "#888888"             # HTML table rules (visible on dark UI AND white export)
    toggle_on = "#2e6b45"              # enabled (DP step) toggle button
    toggle_off = "#2b2d31"             # disabled toggle button (neutral dark)

    # Column-type icon colours (also read on the light pastel column tags)
    type_numeric = "#5b9bd5"
    type_nominal = "#e57373"
    type_ordinal = "#81c784"
    type_id = "#b388d9"


class Style:
    font_regular = _font_regular
    font_result_label = _font_result_label
    font_result_element_label = _font_result_element_label

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

        # Legacy borders (to be deprecated)
        border_data_analysis = f"5px solid {Scheme.accent_blue}"  # Todo deprecate
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

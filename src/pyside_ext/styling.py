#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from enum import Enum


def css(selector: str = "#id", **kwargs):
    properties = "\n".join(f"\t{key.replace('_', '-')}: {value};" for key, value in kwargs.items())
    return f"{selector}{{\n{properties}\n}}"


class Style:
    class Color(Enum):
        def __str__(self):
            return str(self.value)

        Window = "palette(Window)"  # light gray - The general background for widgets
        WindowText = "palette(WindowText)"  # black - Main text drawn on WINDOW surfaces
        Button = "palette(Button)"  # light gray - Background for buttons, checkboxes, radio buttons
        # ButtonText = "palette(ButtonText)"  # black - Text on buttons (and the “caption” of many controls)
        Base = "palette(Base)"  # white - Background for editable fields
        AlternateBase = "palette(AlternateBase)"  # lighter gray - Alternate background
        Text = "palette(Text)"  # black - Main text on Base surfaces
        Highlight = "palette(Highlight)"  # blue - Background for selected items
        HighlightedText = "palette(HighlightedText)"  # white - Text of selected items

    class FontFamily(Enum):
        def __str__(self):
            return str(self.value)

        SegoeUI = "Segoe UI"

    class FontSize(Enum):
        def __str__(self):
            return str(self.value)

        smaller = "10pt"
        regular = "12pt"
        larger = "14pt"

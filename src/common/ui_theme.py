#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

# Qt-free so it can be imported before the QApplication exists (the launcher reads IS_DARK_THEME
# to pick the window color scheme before creating the app). Every key here is consumed by
# src/pyside_ext/styling.py (Scheme / Style.Color); the active theme is applied at import time, so
# a change takes effect on the next start.

from src.common.config import read_theme_name

LIGHT = {
    # Surfaces
    "surface_panel": "#f0f0f0",
    "surface_main": "#ffffff",
    "surface_edit": "#ffffff",
    "surface_not_selected": "#f5f5f5",
    "surface_elevated": "#eeeeee",
    # Borders
    "border": "#eeeeee",
    "border_elevated": "#cccccc",
    # Text / glyphs
    "text": "#000000",
    "text_secondary": "#666666",
    "text_on_light": "#000000",
    "tool_glyph": "#888888",
    # Accents
    "accent": "#0055ff",
    "selection": "#cfe3ff",
    "danger": "#770000",
    # Removed-row text in the data preview: vivid red on the light paper.
    "removed_row": "#ee0000",
    # Brand color for study titles (legible dark gold on the light paper)
    "title_brand": "#007",
    # Misc
    "overlay": "rgba(0,11,22,0.4)",
    "table_rule": "black",
    "toggle_on": "#cdeacd",
    "toggle_off": "#e0e0e0",
    # Column-type icon colors
    "type_numeric": "darkblue",
    "type_nominal": "darkred",
    "type_ordinal": "darkgreen",
    "type_id": "#6a1b9a",
}

DARK = {
    # Surfaces
    "surface_panel": "#303030",
    "surface_main": "#151515",
    "surface_edit": "#151515",
    "surface_not_selected": "#ff0000",
    "surface_elevated": "#252525",
    # Borders
    "border": "#333333",
    "border_elevated": "#444444",
    # Text / glyphs
    "text": "#e8e6da",
    "text_secondary": "#9a9a93",
    "text_on_light": "#15233b",
    "tool_glyph": "#a6a6a0",
    # Accents
    "accent": "#aaeedd88",
    "selection": "#3a3320",
    "danger": "#ff6b6b",
    # Removed-row text in the data preview: lighter red, legible on the dark table.
    "removed_row": "#ff6b6b",
    # Brand color for study titles (banner gold)
    "title_brand": "#eedd88",
    # Misc
    "overlay": "rgba(255,255,255,0.1)",
    "table_rule": "#888888",
    "toggle_on": "#2e6b45",
    "toggle_off": "#2b2d31",
    # Column-type icon colors
    "type_numeric": "#5b9bd5",
    "type_nominal": "#e57373",
    "type_ordinal": "#81c784",
    "type_id": "#b388d9",
}

_THEMES = {"light": LIGHT, "dark": DARK}

# .get fallback: an unrecognized theme name (e.g. from a hand-edited ini) defaults to light.
ACTIVE_THEME = _THEMES.get(read_theme_name(), LIGHT)
IS_DARK_THEME = ACTIVE_THEME is DARK

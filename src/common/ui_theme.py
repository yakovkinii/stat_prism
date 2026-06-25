#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""UI colour themes.

Kept deliberately **Qt-free** so it can be imported before the ``QApplication`` exists (the
launcher reads ``IS_DARK_THEME`` to pick the window colour scheme / title-bar mode).

Two palettes with identical keys:
  * ``LIGHT`` — the original StatPrism look.
  * ``DARK``  — the current dark look.

The active theme is chosen in ``statprism.ini`` (``[ui] theme = light|dark``); the change
takes effect on the next start (``Style.Color`` captures the values at import time).

Every key here is consumed by ``src/pyside_ext/styling.py`` (``Scheme`` / ``Style.Color``);
widgets only ever reference ``Style.Color`` tokens, so colours live in exactly one place.
"""

import configparser
from pathlib import Path

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
    "accent_blue": "#aaaaff",
    "selection": "#cfe3ff",
    "danger": "#770000",
    # Misc
    "overlay": "rgba(0,11,22,0.4)",
    "table_rule": "black",
    "toggle_on": "#cdeacd",
    "toggle_off": "#e0e0e0",
    # Column-type icon colours
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
    "accent": "#88eedd88",
    "accent_blue": "#3a5a8c",
    "selection": "#3a3320",
    "danger": "#ff6b6b",
    # Misc
    "overlay": "rgba(255,255,255,0.1)",
    "table_rule": "#888888",
    "toggle_on": "#2e6b45",
    "toggle_off": "#2b2d31",
    # Column-type icon colours
    "type_numeric": "#5b9bd5",
    "type_nominal": "#e57373",
    "type_ordinal": "#81c784",
    "type_id": "#b388d9",
}

_THEMES = {"light": LIGHT, "dark": DARK}
_DEFAULT_THEME = "light"
_INI_NAME = "statprism.ini"


def _ini_candidates() -> list:
    """Where to look for / create the config: next to the running app (current working
    directory) first, then the repository root (for source runs)."""
    return [Path.cwd() / _INI_NAME, Path(__file__).resolve().parents[2] / _INI_NAME]


def _create_default_ini() -> None:
    """Write a default config (next to the running app) when none exists, so the user has a
    file to edit. The .ini is gitignored, so this is per-machine."""
    try:
        _ini_candidates()[0].write_text(
            f"[ui]\n# UI colour theme: light or dark\ntheme = {_DEFAULT_THEME}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def _read_theme_name() -> str:
    """Read ``[ui] theme`` from ``statprism.ini``. If no config exists anywhere, create a
    default one and fall back to the default theme (light)."""
    for path in _ini_candidates():
        try:
            if path.is_file():
                parser = configparser.ConfigParser()
                parser.read(path, encoding="utf-8")
                return parser.get("ui", "theme", fallback=_DEFAULT_THEME).strip().lower()
        except Exception:
            continue
    _create_default_ini()
    return _DEFAULT_THEME


ACTIVE_THEME = _THEMES.get(_read_theme_name(), LIGHT)

IS_DARK_THEME = ACTIVE_THEME is DARK

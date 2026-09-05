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


import configparser
import os
from pathlib import Path

_INI_NAME = "statprism.ini"
_DEFAULT_THEME = "light"


def _env_override(key: str):
    # STATPRISM_<KEY> env var overrides the [ui] setting; the test suite uses this to force a
    # deterministic look (see tests/conftest.py).
    return os.environ.get(f"STATPRISM_{key.upper()}")


def _ini_candidates() -> list:
    # Next to the running app (cwd) first, then the repository root (for source runs).
    return [Path.cwd() / _INI_NAME, Path(__file__).resolve().parents[2] / _INI_NAME]


def _create_default_ini() -> None:
    try:  # writing can fail on a read-only install dir; a missing config is non-fatal
        _ini_candidates()[0].write_text(
            f"[ui]\n# UI color theme: light or dark\ntheme = {_DEFAULT_THEME}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def _writable_ini_path() -> Path:
    for path in _ini_candidates():
        if path.is_file():
            return path
    return _ini_candidates()[0]


def read_theme_name() -> str:
    override = _env_override("theme")
    if override is not None:
        return override.strip().lower()
    for path in _ini_candidates():
        try:  # a candidate may be unreadable (permissions); try the next one
            if path.is_file():
                parser = configparser.ConfigParser()
                parser.read(path, encoding="utf-8")
                return parser.get("ui", "theme", fallback=_DEFAULT_THEME).strip().lower()
        except Exception:
            continue
    _create_default_ini()
    return _DEFAULT_THEME


def read_ui_value(key: str, fallback: str) -> str:
    override = _env_override(key)
    if override is not None:
        return override.strip()
    for path in _ini_candidates():
        try:  # a candidate may be unreadable; try the next one
            if path.is_file():
                parser = configparser.ConfigParser()
                parser.read(path, encoding="utf-8")
                return parser.get("ui", key, fallback=fallback).strip()
        except Exception:
            continue
    return fallback


def write_ui_value(key: str, value: str) -> None:
    path = _writable_ini_path()
    parser = configparser.ConfigParser()
    try:  # an existing file may be unreadable/corrupt; start fresh
        if path.is_file():
            parser.read(path, encoding="utf-8")
    except Exception:
        parser = configparser.ConfigParser()
    if not parser.has_section("ui"):
        parser.add_section("ui")
    parser.set("ui", key, value)
    try:  # the install dir can be read-only; failing to persist a setting is non-fatal
        with path.open("w", encoding="utf-8") as handle:
            parser.write(handle)
    except Exception:
        pass


def read_language(fallback: str = "en") -> str:
    return read_ui_value("language", fallback)


def read_plot_theme(fallback: str = "Default") -> str:
    return read_ui_value("plot_theme", fallback)


def read_ui_scale(default: float = 1.0) -> float:
    """The user's UI zoom factor (applied via QT_SCALE_FACTOR at startup). Clamped to a sane range;
    an unreadable/garbage value falls back to the default."""
    try:
        scale = float(read_ui_value("ui_scale", str(default)))
    except ValueError:
        return default
    return min(3.0, max(0.5, scale))


def read_auto_recalculate(default: bool = False) -> bool:
    value = read_ui_value("auto_recalculate", "true" if default else "false").strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return default  # unrecognized value in the ini -> fall back to the default

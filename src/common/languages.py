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


from enum import Enum


class Languages(Enum):
    EN = "en"
    UA = "ua"


class Language:
    def __init__(self, language: Languages = Languages.EN):
        self.language = language

    def set_language(self, language: Languages):
        self.language = language

    def is_en(self):
        return self.language == Languages.EN

    def is_ua(self):
        return self.language == Languages.UA


def _initial_language() -> Languages:
    """Start in the language saved in statprism.ini (falls back to English)."""
    from src.common.ui_theme import read_language

    try:
        return Languages(read_language())
    except Exception:
        return Languages.EN


LANGUAGE = Language(_initial_language())

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


def css(selector: str = "#id", **kwargs):
    properties = "\n".join(f"\t{key.replace('_', '-')}: {value};" for key, value in kwargs.items())
    return f"{selector}{{\n{properties}\n}}"


class HTML:
    @staticmethod
    def div(contents: str, **kwargs):
        style = "; ".join(f"{key.replace('_', '-')}: {value}" for key, value in kwargs.items())
        return f'<div style="{style}">{contents}</div>'

    @staticmethod
    def bold(contents: str):
        return f"<b>{contents}</b>"

    @staticmethod
    def hr():
        return "<hr>"

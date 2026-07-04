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


from src.common.translations import t


class ColumnNumbering:
    """Optional per-study numbering of variable/column names in result tables.

    When enabled, dataset column names are rendered as 1, 2, 3, ... and the
    name <-> number legend is appended to the table Note. When disabled, every
    method is a pass-through, so call sites can use it unconditionally.

    Build it from the ordered list of names that appear in the table headers /
    row labels (for cross tables, pass the de-duplicated union of both sets so a
    variable that appears on both axes gets a single number)."""

    def __init__(self, names, enabled: bool):
        self.enabled = bool(enabled)
        self._map = {}
        if self.enabled:
            i = 1
            for name in names:
                if name not in self._map:
                    self._map[name] = str(i)
                    i += 1

    def label(self, name):
        """The display label for `name` (its number when enabled, else the name)."""
        if not self.enabled:
            return name
        return self._map.get(name, name)

    def legend(self) -> str:
        """The 'number = «name»' legend sentence, or '' when disabled/empty."""
        if not self.enabled or not self._map:
            return ""
        items = "; ".join(f"{num} = «{name}»" for name, num in self._map.items())
        return t("common.column_numbering.legend", items=items)

    def append_to_note(self, note: str) -> str:
        """Append the legend to an existing table Note (space-separated)."""
        legend = self.legend()
        if not legend:
            return note
        if note:
            return f"{note} {legend}"
        return legend

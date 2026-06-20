#  Copyright (c) 2023 StatPrism Team. All rights reserved.


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

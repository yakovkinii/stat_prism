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


class BaseResultElement:
    # Raw numeric data behind this element, attached where the element is populated so a benchmark
    # can drive the real recalculate_*_study() and read the exact numbers that went into the table
    # (keyed by a "kind" tag) instead of re-deriving them. Transient: the GUI recompute wrapper calls
    # BaseResult.drop_numeric_supplement() once the result has rendered, and HTMLTableV2.__getstate__
    # drops it so it is never serialized.
    numeric_supplement = None

    def get_html(self):
        return ...

    def add_numeric_supplement(self, supplement):
        """Attach a dict of the raw numbers behind this element (tagged with a "kind")."""
        self.numeric_supplement = supplement

    def drop_numeric_supplement(self):
        self.numeric_supplement = None

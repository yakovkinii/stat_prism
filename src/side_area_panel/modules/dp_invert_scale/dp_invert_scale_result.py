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


import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Invert scale</b><br>"
    "Reverse-scores the selected columns: each value x becomes (reference &minus; x). With no "
    "reference, it uses (max + min) of the column, so e.g. a 1&ndash;5 Likert item maps 1&harr;5, "
    "2&harr;4, 3&harr;3. Use it to fix reverse-keyed items before building a scale."
)


@attrs.define
class InvertScaleStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    reference = attrs.field(default=None)
    replace_in_place = attrs.field(default=None)

    def __getstate__(self):
        return {field.name: getattr(self, field.name) for field in attrs.fields(type(self))}

    def __setstate__(self, state):
        # Support save files pickled before replace_in_place was added: attrs' generated
        # __setstate__ leaves a missing field unset, so a later attrs.asdict() raises
        # AttributeError. Seed every field with its default first, then apply the pickle.
        fields = attrs.fields(type(self))
        if isinstance(state, tuple):
            state = dict(zip([field.name for field in fields], state))
        for field in fields:
            object.__setattr__(self, field.name, state.get(field.name, field.default))


class InvertScaleResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: InvertScaleStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Invert Scale"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = InvertScaleStudyConfig
        self.config: InvertScaleStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        columns = cfg.column_selector[0] if cfg.column_selector else []
        reference = cfg.reference
        reference_text = str(reference) if reference is not None else "max + min (auto)"
        parts = [
            f"Columns ({len(columns)}): " + (", ".join(columns) if columns else "none"),
            f"Inverted as: ({reference_text}) − x",
            "Mode: replace in place" if getattr(cfg, "replace_in_place", False) else "Mode: new (inverted) column",
        ]
        self.description = "<br>".join(parts)

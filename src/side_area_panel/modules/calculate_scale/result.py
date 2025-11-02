#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_method_noarg
from src.side_area_panel.modules.common.result.registry import BaseResult


class CalculateScaleStudyConfig:
    def __init__(
        self,
        # data=None,
        selected_columns=None,
        mapping_settings=None,
        invert_settings=None,
        aggregation_type="sum",
        new_scale_name="new scale",
        rename_columns=True,
        global_mapping_settings=None,
        global_invert_reference=None,
    ):
        from src.data.data_manager import DATA_MANAGER

        # if data is None:
        #     data = DATA_MANAGER.get_latest_data()
        # self.data = data

        if selected_columns is None:
            selected_columns = []
        self.selected_columns = selected_columns

        # mapping_settings: {column_name: {original_value: mapped_number}}
        if mapping_settings is None:
            mapping_settings = {}
        self.mapping_settings = mapping_settings

        # invert_settings: {column_name: {"enabled": bool, "reference": float}}
        if invert_settings is None:
            invert_settings = {}
        self.invert_settings = invert_settings

        # Aggregation type: "sum" or "mean"
        self.aggregation_type = aggregation_type

        # New scale name
        self.new_scale_name = new_scale_name

        # Whether to rename selected columns
        self.rename_columns = rename_columns

        # Global settings for batch operations
        if global_mapping_settings is None:
            global_mapping_settings = {}
        self.global_mapping_settings = global_mapping_settings

        if global_invert_reference is None:
            global_invert_reference = 0.0
        self.global_invert_reference = global_invert_reference


class CalculateScaleResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CalculateScaleStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Calculate Scale"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: CalculateScaleStudyConfig = config
        self.needs_update: bool = False
        self.description = self._make_description()

        self.data = None

    def _make_description(self):
        lines = []

        # Add selected columns info
        if self.config.selected_columns:
            lines.append(f"Columns: {', '.join(self.config.selected_columns)}")

        # Add aggregation type
        lines.append(f"Aggregation: {self.config.aggregation_type}")

        # Add new scale name
        lines.append(f"New scale: {self.config.new_scale_name}")

        # Add mapping info - show actual mappings
        active_mappings = {}
        for col_name, mapping in self.config.mapping_settings.items():
            if mapping:  # Not empty
                # Check if this is an identity mapping
                is_identity = all(
                    str(key) == str(value)
                    or (
                        isinstance(value, (int, float))
                        and isinstance(key, str)
                        and str(key) == str(int(value))
                        and float(key) == value
                    )
                    for key, value in mapping.items()
                )
                if not is_identity:
                    active_mappings[col_name] = mapping

        if active_mappings:
            lines.append("Value mappings:")
            for col_name, mapping in active_mappings.items():
                mapping_strs = []
                for original, mapped in sorted(mapping.items()):
                    if str(original) != str(mapped):
                        mapping_strs.append(f"'{original}' → {mapped}")
                if mapping_strs:
                    lines.append(f"  {col_name}: {', '.join(mapping_strs)}")

        # Add inversion info
        inverted_cols = [col for col, settings in self.config.invert_settings.items() if settings.get("enabled", False)]
        if inverted_cols:
            invert_info = []
            for col in inverted_cols:
                ref = self.config.invert_settings[col].get("reference", 0.0)
                invert_info.append(f"{col} (ref: {ref})")
            lines.append(f"Inverted: {', '.join(invert_info)}")

        # Add renaming info
        if self.config.rename_columns:
            lines.append("Columns will be renamed")

        return "\n".join(lines)

    @log_method_noarg
    def update_description(self):
        self.description = self._make_description()

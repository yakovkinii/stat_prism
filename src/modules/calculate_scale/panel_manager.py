#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from src.side_area_panel.registry import PanelRegistry


class PanelManager:
    """Manages panel configuration and data processing for calculate scale module"""

    @staticmethod
    def configure_mapping_panel(
        col_name: str,
        base_data: pd.DataFrame,
        config: Any,
        caller_index: int,
        finished_handler: Callable,
        is_global: bool = False,
    ) -> None:
        """Configure and open mapping panel for a column or global settings"""
        if is_global:
            unique_values = PanelManager._get_all_unique_values(base_data, config.selected_columns)
            combined_mapping = PanelManager._create_combined_mapping(unique_values, config)
            panel_title = "Global Mapping"
        else:
            col_data = base_data[col_name].data_series
            unique_values = sorted(col_data.unique())
            combined_mapping = config.mapping_settings.get(col_name, {})
            panel_title = col_name

        if not unique_values:
            logging.info(f"No values to configure mapping for: {panel_title}")
            return

        PanelRegistry.MAPPING.ui_instance.configure(
            column_name=panel_title,
            unique_values=unique_values,
            current_mapping=combined_mapping,
            caller_index=caller_index,
            finished_handler=finished_handler,
        )
        PanelManager._activate_panel(PanelRegistry.MAPPING)

    @staticmethod
    def configure_inversion_panel(
        col_name: str,
        base_data: pd.DataFrame,
        config: Any,
        caller_index: int,
        finished_handler: Callable,
        is_global: bool = False,
    ) -> None:
        """Configure and open inversion panel for a column or global settings"""
        if is_global:
            min_val, max_val, unique_values = PanelManager._get_global_value_range(base_data, config)
            current_reference = PanelManager._get_global_reference(config)
            panel_title = "Global Inversion"
        else:
            min_val, max_val, unique_values = PanelManager._get_column_value_range(col_name, base_data, config)
            current_reference = config.invert_settings.get(col_name, {}).get("reference")
            panel_title = col_name

        if min_val is None or max_val is None:
            logging.info(f"No valid data range for inversion: {panel_title}")
            return

        PanelRegistry.INVERSION_CONFIG.ui_instance.configure(
            column_name=panel_title,
            min_value=min_val,
            max_value=max_val,
            current_reference=current_reference or (min_val + max_val),
            caller_index=caller_index,
            finished_handler=finished_handler,
            unique_values=unique_values,
        )
        PanelManager._activate_panel(PanelRegistry.INVERSION_CONFIG)

    @staticmethod
    def _get_all_unique_values(base_data: pd.DataFrame, columns: List[str]) -> List:
        """Get all unique values from selected columns"""
        all_unique_values = set()
        for col_name in columns:
            col_data = base_data[col_name].data_series
            unique_vals = col_data.dropna().unique()
            all_unique_values.update(unique_vals)

        try:
            return sorted(list(all_unique_values), key=str)
        except Exception:
            return list(all_unique_values)

    @staticmethod
    def _create_combined_mapping(unique_values: List, config: Any) -> Dict:
        """Create a combined mapping from existing mappings"""
        combined_mapping = {}
        for value in unique_values:
            # Try to find existing mapping
            found_mapping = None
            for col_name in config.selected_columns:
                if col_name in config.mapping_settings and value in config.mapping_settings[col_name]:
                    found_mapping = config.mapping_settings[col_name][value]
                    break

            if found_mapping is not None:
                combined_mapping[value] = found_mapping
            else:
                try:
                    combined_mapping[value] = float(value)
                except (ValueError, TypeError):
                    combined_mapping[value] = float(unique_values.index(value) + 1)
        return combined_mapping

    @staticmethod
    def _get_column_value_range(col_name: str, base_data: pd.DataFrame, config: Any) -> tuple:
        """Get min, max and unique values for a column"""
        col_data = base_data[col_name].data_series

        if col_name in config.mapping_settings and config.mapping_settings[col_name]:
            mapped_data = col_data.map(config.mapping_settings[col_name])
            clean_data = mapped_data.dropna()
        else:
            clean_data = col_data.dropna()

        if len(clean_data) > 0:
            return clean_data.min(), clean_data.max(), sorted(clean_data.unique())
        return None, None, []

    @staticmethod
    def _get_global_value_range(base_data: pd.DataFrame, config: Any) -> tuple:
        """Get global min, max and unique values across all selected columns"""
        all_min_vals = []
        all_max_vals = []
        all_unique_values = set()

        for col_name in config.selected_columns:
            min_val, max_val, unique_vals = PanelManager._get_column_value_range(col_name, base_data, config)
            if min_val is not None and max_val is not None:
                all_min_vals.append(min_val)
                all_max_vals.append(max_val)
                all_unique_values.update(unique_vals)

        if all_min_vals and all_max_vals:
            return min(all_min_vals), max(all_max_vals), sorted(list(all_unique_values))
        return None, None, []

    @staticmethod
    def _get_global_reference(config: Any) -> Optional[float]:
        """Find existing global reference from any column"""
        for col_name in config.selected_columns:
            if col_name in config.invert_settings:
                ref = config.invert_settings[col_name].get("reference")
                if ref is not None:
                    return ref
        return None

    @staticmethod
    def _activate_panel(panel):
        """Activate the given settings panel"""
        root_class = PanelRegistry.MAPPING.ui_instance.root_class
        root_class.action_activate_panel_by_index(panel.settings_stacked_widget_index)

    @staticmethod
    def calculate_invert_reference(col_name: str, base_data: pd.DataFrame, config: Any) -> float:
        """Calculate invert reference for a column after applying mappings"""
        min_val, max_val, _ = PanelManager._get_column_value_range(col_name, base_data, config)
        if min_val is not None and max_val is not None:
            return min_val + max_val
        return 0.0

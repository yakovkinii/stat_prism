#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.messages import MessageType
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.calculate_scale.result import CalculateScaleResult, CalculateScaleStudyConfig
from src.modules.common.result.registry import RESULTS
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_blocks import ColumnBlocksVisualizer
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.markup import css
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title
from src.pyside_ext.elements.title_editable import ColumnNameEditable
from src.settings_panel.registry import PanelRegistry


class CalculateScale(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Calculate Scale"),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Columns for scale:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=10,
                    ),
                ],
            ),
            "column_blocks": ColumnBlocksVisualizer(),
            "aggregation_type": ComboBox("Aggregation type: "),
            "new_scale_name": ColumnNameEditable("new scale"),
            "rename_columns": LargeCheckbox(label_text="Auto rename questions"),
        }
        self.setup(stretch=True)

        # Configure element spacing using CSS margins
        self._apply_element_spacing()

        # Configure aggregation type options
        self.elements["aggregation_type"].configure(["sum", "mean"])
        
        # Inject column blocks with handler
        self.elements["column_blocks"].inject(self.widget, self.handler, "column_blocks")

        # Initialize message handlers
        self._init_message_handlers()

    def _apply_element_spacing(self):
        """Apply spacing to container widget to affect all child elements"""
        self.widget.setStyleSheet(
            css(
                "QWidget > QWidget",  # Apply to direct children widgets
                margin_top="10px",
                margin_bottom="10px",
            )
        )

    def _init_message_handlers(self):
        """Initialize message handlers map"""
        self.message_handlers = {
            MessageType.STATE_CHANGED: {
                "column_selector": self._handle_column_selection,
                "aggregation_type": self._handle_aggregation_change,
                "new_scale_name": self._handle_scale_name_change,
                "rename_columns": self._handle_rename_toggle,
                "column_blocks": self._handle_column_blocks_state,
            },
            MessageType.EDITING_FINISHED: {
                "column_selector": self._handle_column_selection,
            },
            MessageType.CLICKED: {
                "column_blocks": self._handle_column_blocks_click,
            }
        }

    def _handle_column_selection(self, message):
        """Handle column selection changes"""
        selected_columns = self.elements["column_selector"].get_selected_columns()[0]
        config = RESULTS[self.result_id].config
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)

        # Update selected columns
        config.selected_columns = selected_columns

        # Clean up settings for removed columns
        config.mapping_settings = {
            col: settings for col, settings in config.mapping_settings.items() 
            if col in selected_columns
        }
        config.invert_settings = {
            col: settings for col, settings in config.invert_settings.items() 
            if col in selected_columns
        }

        # Initialize settings for new columns
        for col_name in selected_columns:
            if col_name not in config.mapping_settings:
                col_data = base_data[col_name].data_series
                if not pd.api.types.is_numeric_dtype(col_data):
                    unique_vals = col_data.dropna().unique()
                    config.mapping_settings[col_name] = self._create_default_mapping(unique_vals)
                else:
                    config.mapping_settings[col_name] = {}

            if col_name not in config.invert_settings:
                config.invert_settings[col_name] = {
                    "enabled": False,
                    "reference": PanelManager.calculate_invert_reference(col_name, base_data, config)
                }

        self.configure(result_id=self.result_id)
        self.recalculate()

    def _handle_column_blocks_state(self, message):
        """Handle column blocks state changes"""
        payload = message.payload
        action = payload.get("action")
        col_name = payload.get("column")
        config = RESULTS[self.result_id].config

        if action == "mapping_updated":
            config.mapping_settings[col_name] = payload["mapping"]
        elif action == "inversion_updated":
            if col_name not in config.invert_settings:
                config.invert_settings[col_name] = {}
            config.invert_settings[col_name]["reference"] = payload["reference"]
        elif action == "invert_toggled":
            if col_name not in config.invert_settings:
                config.invert_settings[col_name] = {}
            config.invert_settings[col_name]["enabled"] = payload["enabled"]

        self.recalculate()

    def _handle_column_blocks_click(self, message):
        """Handle column blocks click events"""
        payload = message.payload
        action = payload.get("action")
        col_name = payload.get("column")
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)
        config = RESULTS[self.result_id].config

        action_handlers = {
            "configure_mapping": lambda: PanelManager.configure_mapping_panel(
                col_name, base_data, config, self.stacked_widget_index, self._mapping_finished_handler
            ),
            "configure_inversion": lambda: PanelManager.configure_inversion_panel(
                col_name, base_data, config, self.stacked_widget_index, self._inversion_finished_handler
            ),
            "configure_global_mapping": lambda: PanelManager.configure_mapping_panel(
                col_name, base_data, config, self.stacked_widget_index, 
                self._global_mapping_finished_handler, is_global=True
            ),
            "configure_global_inversion": lambda: PanelManager.configure_inversion_panel(
                col_name, base_data, config, self.stacked_widget_index,
                self._global_inversion_finished_handler, is_global=True
            ),
        }

        if action in action_handlers:
            action_handlers[action]()

    def _handle_aggregation_change(self, message):
        """Handle aggregation type changes"""
        config = RESULTS[self.result_id].config
        config.aggregation_type = self.elements["aggregation_type"].combo_box.currentText()
        self.recalculate()

    def _handle_scale_name_change(self, message):
        """Handle scale name changes"""
        config = RESULTS[self.result_id].config
        config.new_scale_name = self.elements["new_scale_name"].widget.text().strip() or "new scale"
        self.recalculate()

    def _handle_rename_toggle(self, message):
        """Handle rename checkbox toggle"""
        config = RESULTS[self.result_id].config
        config.rename_columns = self.elements["rename_columns"].widget.isChecked()
        self.recalculate()

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        config: CalculateScaleStudyConfig = RESULTS[result_id].config

        # Always use the data before this result for UI
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)

        # Configure column selector
        self.elements["column_selector"].configure(
            columns=base_data.get_all_columns_as_column_types(),
            selected_columns_list=[config.selected_columns],
        )

        # Configure column blocks
        self.elements["column_blocks"].configure(
            columns=config.selected_columns,
            mapping_settings=config.mapping_settings,
            invert_settings=config.invert_settings,
        )

        # Configure aggregation type
        aggregation_index = 0 if config.aggregation_type == "sum" else 1
        self.elements["aggregation_type"].combo_box.setCurrentIndex(aggregation_index)

        # Configure new scale name
        self.elements["new_scale_name"].widget.setText(config.new_scale_name)

        # Configure rename checkbox
        self.elements["rename_columns"].widget.setChecked(config.rename_columns)

        self.configuring = False

    @log_method
    def handler(self, message):
        if self.configuring:
            return

        if message.message_type in (MessageType.STATE_CHANGED, MessageType.EDITING_FINISHED):
            if message.caller_id == "column_selector":
                selected_columns = self.elements["column_selector"].get_selected_columns()[0]
                config = RESULTS[self.result_id].config

                # Update selected columns
                config.selected_columns = selected_columns

                # Clean up settings for removed columns
                config.mapping_settings = {
                    col: settings for col, settings in config.mapping_settings.items() if col in selected_columns
                }
                config.invert_settings = {
                    col: settings for col, settings in config.invert_settings.items() if col in selected_columns
                }

                # Initialize default settings for new columns AND reset for all columns
                base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)
                for col_name in selected_columns:
                    # Always reset mapping to default when columns change
                    col_data = base_data[col_name].data_series
                    if not pd.api.types.is_numeric_dtype(col_data):
                        unique_vals = col_data.dropna().unique()
                        config.mapping_settings[col_name] = self._create_default_mapping(unique_vals)
                    else:
                        config.mapping_settings[col_name] = {}

                    # Reset invert settings when mapping changes
                    if col_name not in config.invert_settings:
                        config.invert_settings[col_name] = {"enabled": False, "reference": 0.0}

                    # Recalculate invert reference based on new mapping
                    new_reference = self._calculate_invert_reference_for_column(col_name, base_data, config)
                    config.invert_settings[col_name]["reference"] = new_reference

                self.configure(result_id=self.result_id)
                self.recalculate()
                return

            elif message.caller_id == "column_blocks":
                payload = message.payload
                action = payload.get("action")

                if action == "mapping_updated":
                    col_name = payload["column"]
                    mapping = payload["mapping"]
                    config = RESULTS[self.result_id].config
                    config.mapping_settings[col_name] = mapping
                    self.recalculate()
                    return

                elif action == "inversion_updated":
                    col_name = payload["column"]
                    reference = payload["reference"]
                    config = RESULTS[self.result_id].config
                    if col_name not in config.invert_settings:
                        config.invert_settings[col_name] = {}
                    config.invert_settings[col_name]["reference"] = reference
                    self.recalculate()
                    return

                elif action == "invert_toggled":
                    col_name = payload["column"]
                    enabled = payload["enabled"]
                    config = RESULTS[self.result_id].config
                    if col_name not in config.invert_settings:
                        config.invert_settings[col_name] = {}
                    config.invert_settings[col_name]["enabled"] = enabled
                    self.recalculate()
                    return

            elif message.caller_id == "aggregation_type":
                config = RESULTS[self.result_id].config
                config.aggregation_type = self.elements["aggregation_type"].combo_box.currentText()
                self.recalculate()
                return

            elif message.caller_id == "new_scale_name":
                config = RESULTS[self.result_id].config
                config.new_scale_name = self.elements["new_scale_name"].widget.text().strip() or "new scale"
                self.recalculate()
                return

            elif message.caller_id == "rename_columns":
                config = RESULTS[self.result_id].config
                config.rename_columns = self.elements["rename_columns"].widget.isChecked()
                self.recalculate()
                return

        elif message.message_type == MessageType.CLICKED:
            if message.caller_id == "column_blocks":
                payload = message.payload
                action = payload.get("action")
                col_name = payload.get("column")

                if action == "configure_mapping":
                    self._open_mapping_panel(col_name)
                    return
                elif action == "configure_inversion":
                    self._open_inversion_panel(col_name)
                    return
                elif action == "configure_global_mapping":
                    self._open_global_mapping_panel()
                    return
                elif action == "configure_global_inversion":
                    self._open_global_inversion_panel()
                    return

        super().handler(message)

    def _create_default_mapping(self, unique_values):
        """Create default mapping for string values"""
        mapping = {}
        for i, value in enumerate(sorted(unique_values)):
            try:
                # Try to parse as number
                mapping[value] = float(value)
            except (ValueError, TypeError):
                # Use index + 1 as default
                mapping[value] = float(i + 1)
        return mapping

    def _open_mapping_panel(self, col_name):
        """Open the mapping configuration panel"""
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)
        col_data = base_data[col_name].data_series
        unique_values = sorted(col_data.unique())

        config = RESULTS[self.result_id].config
        current_mapping = config.mapping_settings.get(col_name, {})

        # Configure and open mapping panel
        PanelRegistry.MAPPING.ui_instance.configure(
            column_name=col_name,
            unique_values=unique_values,
            current_mapping=current_mapping,
            caller_index=self.stacked_widget_index,
            finished_handler=self._mapping_finished_handler,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.MAPPING.settings_stacked_widget_index)

    def _open_inversion_panel(self, col_name):
        """Open the inversion configuration panel"""
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)
        col_data = base_data[col_name].data_series

        # Apply mapping first if exists
        config = RESULTS[self.result_id].config
        if col_name in config.mapping_settings and config.mapping_settings[col_name]:
            mapped_data = col_data.map(config.mapping_settings[col_name])
            mapped_data = mapped_data.dropna()
            min_val = mapped_data.min()
            max_val = mapped_data.max()
            unique_values = sorted(mapped_data.unique())
        else:
            clean_data = col_data.dropna()
            min_val = clean_data.min()
            max_val = clean_data.max()
            unique_values = sorted(clean_data.unique())

        current_reference = config.invert_settings.get(col_name, {}).get("reference")

        # Configure and open inversion panel
        PanelRegistry.INVERSION_CONFIG.ui_instance.configure(
            column_name=col_name,
            min_value=min_val,
            max_value=max_val,
            current_reference=current_reference,
            caller_index=self.stacked_widget_index,
            finished_handler=self._inversion_finished_handler,
            unique_values=unique_values,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.INVERSION_CONFIG.settings_stacked_widget_index)

    def _open_global_mapping_panel(self):
        """Open the global mapping configuration panel"""
        config = RESULTS[self.result_id].config
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)

        # Collect ALL unique values from ALL selected columns (including numeric)
        all_unique_values = set()

        for col_name in config.selected_columns:
            col_data = base_data[col_name].data_series
            unique_vals = col_data.dropna().unique()
            all_unique_values.update(unique_vals)

        if not all_unique_values:
            logging.info("No columns to configure mapping for")
            return

        # Convert all values to strings for sorting to avoid type comparison issues
        try:
            unique_values = sorted(list(all_unique_values), key=str)
        except Exception:
            # If sorting fails, convert to list without sorting
            unique_values = list(all_unique_values)

        # Create a combined mapping from existing mappings
        combined_mapping = {}
        for value in unique_values:
            # Try to find existing mapping for this value in any column
            found_mapping = None
            for col_name in config.selected_columns:
                if col_name in config.mapping_settings:
                    if value in config.mapping_settings[col_name]:
                        found_mapping = config.mapping_settings[col_name][value]
                        break

            if found_mapping is not None:
                combined_mapping[value] = found_mapping
            else:
                # Create default mapping
                try:
                    combined_mapping[value] = float(value)
                except (ValueError, TypeError):
                    combined_mapping[value] = float(unique_values.index(value) + 1)

        # Configure and open mapping panel with global context
        PanelRegistry.MAPPING.ui_instance.configure(
            column_name="Global Mapping",
            unique_values=unique_values,
            current_mapping=combined_mapping,
            caller_index=self.stacked_widget_index,
            finished_handler=self._global_mapping_finished_handler,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.MAPPING.settings_stacked_widget_index)

    def _open_global_inversion_panel(self):
        """Open the global inversion configuration panel"""
        config = RESULTS[self.result_id].config
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)

        # Calculate a global reference value based on all selected columns
        all_min_vals = []
        all_max_vals = []
        all_unique_values = set()

        for col_name in config.selected_columns:
            col_data = base_data[col_name].data_series

            # Apply mapping first if exists
            if col_name in config.mapping_settings and config.mapping_settings[col_name]:
                mapped_data = col_data.map(config.mapping_settings[col_name])
                # Skip NaN values when calculating min/max
                mapped_data = mapped_data.dropna()
                if len(mapped_data) > 0:
                    all_min_vals.append(mapped_data.min())
                    all_max_vals.append(mapped_data.max())
                    all_unique_values.update(mapped_data.unique())
            else:
                clean_data = col_data.dropna()
                if len(clean_data) > 0:
                    all_min_vals.append(clean_data.min())
                    all_max_vals.append(clean_data.max())
                    all_unique_values.update(clean_data.unique())

        if all_min_vals and all_max_vals:
            global_min = min(all_min_vals)
            global_max = max(all_max_vals)
            global_unique_values = sorted(list(all_unique_values))

            # Find existing global reference if any
            current_global_reference = None
            for col_name in config.selected_columns:
                if col_name in config.invert_settings:
                    ref = config.invert_settings[col_name].get("reference")
                    if ref is not None:
                        current_global_reference = ref
                        break

            # Use calculated reference if no existing one found
            if current_global_reference is None:
                current_global_reference = global_min + global_max

            # Configure and open inversion panel with global context
            PanelRegistry.INVERSION_CONFIG.ui_instance.configure(
                column_name="Global Inversion",
                min_value=global_min,
                max_value=global_max,
                current_reference=current_global_reference,
                caller_index=self.stacked_widget_index,
                finished_handler=self._global_inversion_finished_handler,
                unique_values=global_unique_values,
            )
            self.root_class.action_activate_panel_by_index(PanelRegistry.INVERSION_CONFIG.settings_stacked_widget_index)

    def _calculate_invert_reference_for_column(self, col_name, base_data, config):
        """Calculate invert reference for a column after applying mappings"""
        col_data = base_data[col_name].data_series

        # Apply mapping first if exists
        if col_name in config.mapping_settings and config.mapping_settings[col_name]:
            mapped_data = col_data.map(config.mapping_settings[col_name])
            clean_data = mapped_data.dropna()
        else:
            clean_data = col_data.dropna()

        if len(clean_data) > 0:
            return clean_data.min() + clean_data.max()
        return 0.0

    def _global_mapping_finished_handler(self, col_name, mapping):
        """Handle global mapping configuration completion"""
        config = RESULTS[self.result_id].config
        base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)

        # Apply the mapping to ALL columns that contain the mapped values
        for column_name in config.selected_columns:
            col_data = base_data[column_name].data_series
            # Check if this column contains any of the mapped values
            unique_vals = set(col_data.dropna().unique())
            mapped_vals = set(mapping.keys())
            if unique_vals.intersection(mapped_vals):
                # Create column-specific mapping with only relevant values
                column_mapping = {}
                for val in unique_vals:
                    if val in mapping:
                        column_mapping[val] = mapping[val]
                config.mapping_settings[column_name] = column_mapping

        # Reset all invert references since global mapping changed - trigger for each column individually
        for column_name in config.selected_columns:
            if column_name in config.invert_settings:
                new_reference = self._calculate_invert_reference_for_column(column_name, base_data, config)
                config.invert_settings[column_name]["reference"] = new_reference

        self.configure(result_id=self.result_id)
        self.recalculate()

    def _global_inversion_finished_handler(self, col_name, reference):
        """Handle global inversion configuration completion"""
        config = RESULTS[self.result_id].config

        # Apply the reference to all columns and enable inversion
        for column_name in config.selected_columns:
            if column_name not in config.invert_settings:
                config.invert_settings[column_name] = {}
            config.invert_settings[column_name]["reference"] = reference
            config.invert_settings[column_name]["enabled"] = True

        self.configure(result_id=self.result_id)
        self.recalculate()

    def _mapping_finished_handler(self, col_name, mapping):
        """Handle mapping configuration completion"""
        config = RESULTS[self.result_id].config
        config.mapping_settings[col_name] = mapping

        # Reset invert reference when mapping changes
        if col_name in config.invert_settings:
            base_data = DATA_MANAGER.get_data_before_result_id(self.result_id)
            new_reference = self._calculate_invert_reference_for_column(col_name, base_data, config)
            config.invert_settings[col_name]["reference"] = new_reference

        self.elements["column_blocks"].update_mapping_settings(col_name, mapping)
        self.recalculate()

    def _inversion_finished_handler(self, col_name, reference):
        """Handle inversion configuration completion"""
        config = RESULTS[self.result_id].config
        if col_name not in config.invert_settings:
            config.invert_settings[col_name] = {"enabled": True}
        config.invert_settings[col_name]["reference"] = reference
        self.elements["column_blocks"].update_invert_reference(col_name, reference)
        self.recalculate()

    @log_method
    def recalculate(self):
        if self.configuring:
            return

        config: CalculateScaleStudyConfig = RESULTS[self.result_id].config
        selected_columns = config.selected_columns

        if not selected_columns:
            # No columns selected, set placeholder
            result: CalculateScaleResult = RESULTS[self.result_id]
            result.config = config
            result.set_placeholder("Please select columns for the scale")
            result.needs_update = True
            self.root_class.main_area_panel.refresh_result(self.result_id)
            return

        # Use the data before this result for calculation
        data = DATA_MANAGER.get_data_before_result_id(self.result_id).copy()

        col_data = []
        col_names = []
        processed_names = []

        # Apply mappings and inversions permanently to the actual data columns
        for col_name in selected_columns:
            dc = next((c for c in data.columns if c.column_name == col_name), None)
            if dc is not None:
                # Apply mapping if exists
                if col_name in config.mapping_settings and config.mapping_settings[col_name]:
                    dc.data_series = dc.data_series.map(config.mapping_settings[col_name])
                    # Update column type and dtype after mapping
                    dc.check_and_update_column_dtype()

                # Apply inversion if enabled
                if col_name in config.invert_settings and config.invert_settings[col_name].get("enabled", False):
                    reference = config.invert_settings[col_name].get("reference", 0.0)
                    dc.data_series = reference - dc.data_series

                    # Cast back to int if both reference and values are integers AND no NaN values
                    if (
                        reference == int(reference)
                        and pd.notna(dc.data_series).all()
                        and dc.data_series.apply(  # Check for NaN values first
                            lambda x: x == int(x) if pd.notna(x) else False
                        ).all()
                    ):
                        dc.data_series = dc.data_series.astype(int)

                    # Update column type and dtype after inversion
                    dc.check_and_update_column_dtype()

                # Use the modified data series for scale calculation
                col_data.append(dc.data_series.copy())
                col_names.append(col_name)

                # Prepare processed name for renaming
                if config.rename_columns:
                    processed_names.append(f"{config.new_scale_name} Q{len(processed_names) + 1}")

        if col_data:
            # Calculate the scale
            df = pd.concat(col_data, axis=1)
            df.columns = col_names

            if config.aggregation_type == "mean":
                new_scale = df.mean(axis=1)
            else:  # sum
                new_scale = df.sum(axis=1)

            # Create new column
            new_col = DataColumn.initialize_from_series(new_scale.rename(config.new_scale_name))

            # Set color for selected columns (using color index 1 - light red)
            for col_name in selected_columns:
                col_idx = next((i for i, c in enumerate(data.columns) if c.column_name == col_name), None)
                if col_idx is not None:
                    data.columns[col_idx].color = 1

            # Rename columns if requested
            if config.rename_columns and processed_names:
                for i, col_name in enumerate(col_names):
                    col_idx = next((idx for idx, c in enumerate(data.columns) if c.column_name == col_name), None)
                    if col_idx is not None and i < len(processed_names):
                        data.columns[col_idx].column_name = processed_names[i]

            # Insert new scale column right after the last selected column
            last_selected_index = data.find_last_column_index(selected_columns)
            if last_selected_index >= 0:
                data.insert_column_after_index(new_col, last_selected_index)
            else:
                # Fallback: append at the end if selected columns not found
                data.columns.append(new_col)
                data.update_lookups()

        config.data = data
        result: CalculateScaleResult = RESULTS[self.result_id]
        result.config = config
        result.update_description()
        result.needs_update = True
        self.root_class.main_area_panel.refresh_result(self.result_id)

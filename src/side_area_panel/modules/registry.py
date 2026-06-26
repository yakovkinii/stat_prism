#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs


class ModuleType(Enum):
    RAW_DATA = "RAW_DATA"
    DATA_PROCESSING = "DATA_PROCESSING"
    DATA_ANALYSIS = "DATA_ANALYSIS"


@attrs.define
class ModuleRegistryItem:
    display_name: str
    ui_class: any = None
    result_class: any = None
    config_class: any = None
    main_function: any = None
    ui_instance: any = None
    settings_stacked_widget_index: int = None
    icon_path: str = None
    module_type: ModuleType = ModuleType.DATA_ANALYSIS


class ModuleRegistry(Enum):
    # Order matters: it sets both the "add study" button order and (positionally) each
    # module's settings-panel index. Modules are grouped so related ones sit together and
    # share an icon, and the overall flow follows data manipulation -> analysis.
    RAW_DATA = ModuleRegistryItem(
        display_name="Raw Data",
        icon_path="msc.database",
        module_type=ModuleType.RAW_DATA,
    )

    # --- Data processing -------------------------------------------------------------
    # Column editing (type / mapping / order / rename) -- shared icon.
    PREPROCESS = ModuleRegistryItem(
        display_name="Preprocess",
        icon_path="mdi6.table-edit",
        module_type=ModuleType.DATA_PROCESSING,
    )

    TRANSFORM = ModuleRegistryItem(
        display_name="Transform Column",
        icon_path="mdi6.table-edit",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Scale construction -- shared icon.
    CALCULATE_SCALE = ModuleRegistryItem(
        display_name="Calculate Scale",
        icon_path="mdi6.scale-balance",
        module_type=ModuleType.DATA_PROCESSING,
    )

    INVERT_SCALE = ModuleRegistryItem(
        display_name="Invert Scale",
        icon_path="mdi6.scale-balance",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Derive a new column -- shared icon.
    FORMULA = ModuleRegistryItem(
        display_name="Formula Column",
        icon_path="mdi6.calculator",
        module_type=ModuleType.DATA_PROCESSING,
    )

    GROUP_VALUES = ModuleRegistryItem(
        display_name="Group Values",
        icon_path="mdi6.calculator",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Expand a categorical column into indicator columns -- shared icon.
    ONE_HOT = ModuleRegistryItem(
        display_name="One-hot encoding",
        icon_path="mdi6.matrix",
        module_type=ModuleType.DATA_PROCESSING,
    )

    SPLIT_MULTISELECT = ModuleRegistryItem(
        display_name="Split Multi-Select",
        icon_path="mdi6.matrix",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Row / missing-value cleaning.
    FILTER = ModuleRegistryItem(
        display_name="Filter",
        icon_path="mdi6.filter-outline",
        module_type=ModuleType.DATA_PROCESSING,
    )

    IMPUTE = ModuleRegistryItem(
        display_name="Impute Missing",
        icon_path="mdi6.bandage",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Outlier detection -- shared icon.
    OUTLIERS = ModuleRegistryItem(
        display_name="Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    GROUPED_OUTLIERS = ModuleRegistryItem(
        display_name="Grouped Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    TWO_D_OUTLIERS = ModuleRegistryItem(
        display_name="2D Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # Structural / synthetic.
    SELECT_ID = ModuleRegistryItem(
        display_name="Select ID Column",
        icon_path="mdi6.key-variant",
        module_type=ModuleType.DATA_PROCESSING,
    )

    BOOTSTRAP = ModuleRegistryItem(
        display_name="Bootstrap Sensitivity",
        icon_path="mdi6.dice-multiple-outline",
        module_type=ModuleType.DATA_PROCESSING,
    )

    # --- Data analysis ---------------------------------------------------------------
    # Describe.
    DESCRIPTIVE = ModuleRegistryItem(
        display_name="Descriptive Statistics",
        icon_path="ph.note",
    )

    MULTIPLE_RESPONSE = ModuleRegistryItem(
        display_name="Multiple Response",
        icon_path="mdi6.format-list-checks",
    )

    # Association between two variables -- shared icon.
    CONTINGENCY = ModuleRegistryItem(
        display_name="Contingency Table",
        icon_path="msc.link",
    )

    CORRELATION = ModuleRegistryItem(
        display_name="Correlation",
        icon_path="msc.link",
    )

    # Group comparison -- shared icon.
    MEAN_COMPARISON = ModuleRegistryItem(
        display_name="T-test/ANOVA",
        icon_path="ph.scales",
    )

    PAIRED = ModuleRegistryItem(
        display_name="Paired T-test/ANOVA",
        icon_path="ph.scales",
    )

    # Prediction / modelling.
    REGRESSION = ModuleRegistryItem(
        display_name="Regression",
        icon_path="mdi6.chart-bell-curve-cumulative",
    )

    # Scales & latent structure (EFA / CFA share an icon).
    RELIABILITY = ModuleRegistryItem(
        display_name="Reliability",
        icon_path="mdi6.check-decagram",
    )

    FACTOR_ANALYSIS = ModuleRegistryItem(
        display_name="Exploratory Factor Analysis",
        icon_path="mdi6.chart-bubble",
    )

    CFA = ModuleRegistryItem(
        display_name="Confirmatory Factor Analysis",
        icon_path="mdi6.chart-bubble",
    )

    # Segmentation.
    CLUSTER_ANALYSIS = ModuleRegistryItem(
        display_name="Cluster Analysis",
        icon_path="mdi6.scatter-plot-outline",
    )

    # Study planning.
    POWER_ANALYSIS = ModuleRegistryItem(
        display_name="Power Analysis",
        icon_path="mdi6.calculator-variant-outline",
    )

    @property
    def display_name(self):
        return self.value.display_name

    @property
    def ui_class(self):
        return self.value.ui_class

    @property
    def result_class(self):
        return self.value.result_class

    @property
    def ui_instance(self):
        return self.value.ui_instance

    @property
    def main_function(self):
        return self.value.main_function

    @property
    def settings_stacked_widget_index(self):
        return self.value.settings_stacked_widget_index

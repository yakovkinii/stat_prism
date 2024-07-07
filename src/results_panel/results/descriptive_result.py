from src.core.descriptive.objects import DescriptiveStudyConfig
from src.results_panel.results.base_result import BaseResult
from src.results_panel.results.table_element import TableResultElement
from src.results_panel.results.text_element import TextResultElement


class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title=None, config: DescriptiveStudyConfig = None):
        super().__init__(unique_id)
        self.table = "table"
        self.description = "description"
        self.result_elements = {
            self.table: TableResultElement(
                dataframe=None,
            ),
            self.description: TextResultElement(text=""),
        }
        self.settings_panel_index = settings_panel_index
        if title is None:
            title = "Descriptive "+str(unique_id)
        self.title = title

        if config is None:
            self.config: DescriptiveStudyConfig = DescriptiveStudyConfig(
                selected_columns=[],
            )
        else:
            self.config: DescriptiveStudyConfig = config

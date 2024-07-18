from typing import Dict


class BaseResult:
    def __init__(self, unique_id):
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.result_elements: Dict[str, BaseResultElement] = {}
        # Display title (result selector)
        self.title: str = ...
        # Display title context (result display)
        self.title_context: str = ...
        # Settings panel index for activating the result
        self.settings_panel_index: int = ...
        # Result config
        self.config = ...
        # Flag for updating the result
        self.needs_update: bool = False

    def configure(self, *args, **kwargs):
        pass


class BaseResultElement:
    def __init__(self):
        self.title: str = ...
        self.class_id: str = ...


APA_TABLE_STYLE_CLASSES = """
<style>
      table, th, td, span {
        border-collapse: collapse;
        text-align: left;
        font-size: 12pt;
        font-family: "Times New Roman";
      }
      table{
      margin-bottom: 5px;
      margin-top: 5px;
      }

      td {
        padding: 2px 10px;
      }
      .scrollable {
        overflow-x: auto;
      }
      .thick-border-bottom{
        border-bottom: 2px solid #000;
      }
      .thick-border-top{
        border-top: 2px solid #000;
      }
      .thin-border-left{
        /*border-left: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-right{
        /*border-right: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-top{
        /*border-top: 1px solid rgba(0,0,0,10);*/
      }
      .thin-border-bottom{
        /*border-bottom: 1px solid rgba(0,0,0,10);*/
      }
      .align-right {
        text-align: right;
        padding-right: 0px;
        margin:0px;
      }
      .align-left {
        text-align: left;
        padding-left: 0px;
      }
      .footnote{
        text-align: left;
        margin-left: 10px;
        font-size: 12pt;
        font-family: "Times New Roman";
      }
      .table-name-apa{
        text-align: left;
        margin-left: 0px;
        margin-top:3px;
        margin-bottom:3px;
        font-size: 12pt;
        font-weight: 600;
        font-family: "Times New Roman";
      }
      .table-title-apa{
        text-align: left;
        margin-left: 0px;
        margin-top:3px;
        font-size: 12pt;
        font-style: italic;
        font-family: "Times New Roman";
      }
      .nowrap{
      white-space: nowrap;
      }
      .multilinemm {
        width: 20px; /* Adjust the width as needed */
        word-wrap: break-word;
        white-space: normal; /* Override any existing nowrap */
      }
      </style>
      """

from typing import List



class ResultMetadata:
    def __init__(self, study_id: int, study_options):
        self.study_id = study_id
        self.study_options = study_options


class Result:
    def __init__(self, identifier: int, html: str, metadata: List[ResultMetadata]):
        self.id = identifier
        self.html = html
        self.metadata = metadata

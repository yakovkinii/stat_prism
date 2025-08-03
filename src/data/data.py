#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd


class Data:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

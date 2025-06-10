import pandas as pd 

from loguru import logger
from icecream import ic 
from pathlib import Path

class Table:
    def __init__(self, file_path: Path, sheet_name: str):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def _get(self):
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        return df

    def switch_starting_row(self, starting_row: int, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.iloc[starting_row-1]
        df = df[starting_row:]
        return df
    
    def get(self, starting_row: int=None):
        df = self.switch_starting_row(starting_row, self._get()) if starting_row else self._get()
        return df


class TableMapper:
    def __init__(self, table: pd.DataFrame, mapper: dict):
        self.table = table
        self.mapper = mapper

    def map_values(self):
        
import pandas as pd 

from loguru import logger
from pathlib import Path


class ExcelFile:
    
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path
        self.file_name: str = file_path.name
        


class ExcelSheet(ExcelFile):
    
    def __init__(self, file_path: Path, sheet_name: str):
        super().__init__(file_path)
        self.sheet_name: str = sheet_name
        self.df = pd.read_excel(file_path, sheet_name=sheet_name)
        
    
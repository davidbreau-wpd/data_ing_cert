import pandas as pd

from loguru import logger
from pathlib import Path

database_excel_filename = "2025_Base De Donnée_V1.xlsx"
database_excel_path = Path("P:") / "windmanager" / "00_Share point general" / database_excel_filename

database_TEMP_name = "2025_Base De Donnée_V1.xlsx"
database_TEMP_path = Path('data', 'excel') / database_TEMP_name


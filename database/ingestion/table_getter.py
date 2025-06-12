import os
import pandas as pd 
from sqlalchemy import create_engine
from loguru import logger
from icecream import ic 
from pathlib import Path
from typing import Optional

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
        """
        Filter and rename columns based on the mapper dictionary.
        The mapper should be in format {original_column_name: new_column_name}
        """
        # Select only columns in the mapper and rename them
        columns_to_keep = list(self.mapper.keys())
        
        # Filter and rename in one step
        filtered_df = self.table[columns_to_keep].rename(columns=self.mapper)
        
        return filtered_df


class TableLoader:
    def __init__(self, df: pd.DataFrame, folder_path: str, file_name: str):
        """Initialize TableLoader with a DataFrame and path information.
        Args:
            df: DataFrame to save/load
            folder_path: Directory to save the CSV file
            file_name: Name of the CSV file (without extension)
        """
        self.df = df
        self.folder_path = folder_path
        self.file_name = file_name
        self.full_path = os.path.join(folder_path, f"{file_name}.csv")
        
    def save_to_csv(self, index: bool = False) -> str:
        """Save DataFrame to CSV file.
        Args:
            index: Whether to include index in CSV
        Returns:
            Path to saved CSV file
        """
        os.makedirs(self.folder_path, exist_ok=True)
        self.df.to_csv(self.full_path, index=index)
        logger.info(f"Saved DataFrame to {self.full_path}")
        return self.full_path
    
    def load_to_database(self, 
                         connection_string: str, 
                         table_name: Optional[str] = None, 
                         schema: Optional[str] = None,
                         if_exists: str = 'replace') -> None:
        """Load DataFrame to database.
        Args:
            connection_string: SQLAlchemy connection string
            table_name: Name of the table in database (defaults to file_name if None)
            schema: Database schema (optional)
            if_exists: What to do if table exists ('fail', 'replace', 'append')
        """
        if table_name is None:
            table_name = self.file_name
            
        engine = create_engine(connection_string)
        
        try:
            self.df.to_sql(
                name=table_name,
                con=engine,
                schema=schema,
                if_exists=if_exists,
                index=False
            )
            logger.info(f"Loaded DataFrame to database table {table_name}")
        except Exception as e:
            logger.error(f"Error loading to database: {e}")
            raise
        finally:
            engine.dispose()
    

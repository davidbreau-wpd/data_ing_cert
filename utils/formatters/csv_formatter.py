import pandas as pd
import re

from icecream import ic

class CSVFormatter:
    """ Class containing generic functions to edit CSV's extracted from tables in reports """

    @staticmethod
    def stack_column_in_pairs(df: pd.DataFrame) -> pd.DataFrame:
        """ Merge 1️⃣2️⃣3️⃣4️⃣ DF into 🔢 DF
        Args:
            df(pd.Dataframe): The dataframe that needs stacking formatting
        Returns:
            pd.Dataframe : The stacked dataframe """
            
        df.columns = [i % 2 for i in range(len(df.columns))] 
            # Rename columns to 0,1,0,1 and so on
        
        stacked_pairs = []
        for i in range(0, len(df.columns), 2):
            pair = df.iloc[:, i:i+2]
            stacked_pairs.append(pair)
        stacked_df = pd.concat(stacked_pairs, axis=0)
            # fragments df columns 2 by 2, then merge it all vertically
            
        cl_stacked_df = stacked_df.replace('', pd.NA).dropna()
            # cleans empty rows if pairs of columns have different lengths
        return cl_stacked_df

    @staticmethod
    def merge_continuation_rows(df: pd.DataFrame, new_line: bool = False) -> pd.DataFrame:
        """ Merge rows when cells starts with lower char 
        Args:
            df (pd.DataFrame): To be formatted dataframe
            new_line (bool, optional): Determines if the merge should be done with a new line or a space. Defaults to False.
        Returns:
            pd.DataFrame: _description_
        """
        if df.empty:
            return df.copy()
                # If the dataframe is empty, return it unchanged

        df_processed = df.copy()
        separator = '\n' if new_line else ' '
        last_merge_row_idx = {col_idx: 0 for col_idx in range(len(df_processed.columns))}
            # Initialize a dictionary to keep track of the last row index merged for each column

        for i in range(1, len(df_processed)):
            for col_idx in range(len(df_processed.columns)):
                current_cell_value = df_processed.iloc[i, col_idx]
                starts_with_lowercase = False
                if pd.notna(current_cell_value) and isinstance(current_cell_value, str):
                    cell_str = str(current_cell_value).strip()
                    if cell_str and re.match(r'^[a-z]', cell_str):
                        starts_with_lowercase = True
            # Check if the current cell starts with a lowercase letter
                if starts_with_lowercase:
                    target_row_idx = last_merge_row_idx[col_idx]
                    target_cell_value = df_processed.iloc[target_row_idx, col_idx]
                    target_cell_str = str(target_cell_value) if pd.notna(target_cell_value) else ''
                    current_cell_str = str(current_cell_value).strip()
                    merged_content = f"{target_cell_str}{separator}{current_cell_str}".strip()
                    df_processed.iloc[target_row_idx, col_idx] = merged_content
                    df_processed.iloc[i, col_idx] = ''
                    last_merge_row_idx[col_idx] = target_row_idx
                else:
                    last_merge_row_idx[col_idx] = i
            # Merge rows if the current cell starts with a lowercase letter

        df_cleaned = df_processed[~df_processed.apply(lambda row: all(str(cell).strip() == '' for cell in row), axis=1)]
        return df_cleaned
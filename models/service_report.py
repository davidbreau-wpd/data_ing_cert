import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, logging, pandas as pd, re, numpy as np
from .utils import log_errors, dataframe_required

class _Service_Report:
    """
    Base class for processing service company reports, providing generic and reusable functions
    that can handle various PDF structures across different service companies.
    
    This class offers core functionality for:
    - PDF text and table extraction
    - Data cleaning and transformation pipelines
    - Visualization tools for table verification
    - Standardized data formatting
    
    The methods are designed to be adaptable to different report formats while maintaining
    consistent processing patterns for service industry documentation.
    """
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _get_page(self, page_number: int) -> str:
        """
        Description:
            This method retrieves the text content of a specific page from the PDF document.

        Args:
            page_number (int): The page number to extract text from, starting from 0.

        Returns:
            str: The text content of the specified page.
        """
        with fitz.open(self.file_path) as doc:
            page = doc[page_number].get_text()
            return page


    @log_errors
    def _extract_single_page_table(self, page_number: int, **kwargs) -> camelot.core.Table:
        """
        Description:
            Extracts a table from a specific page of the PDF document using Camelot.

        Args:
            page_number (int): The page number to extract the table from, starting from 0.
            **kwargs: Additional keyword arguments to pass to Camelot's read_pdf function.

        Returns:
            camelot.core.Table: The first table found on the specified page.

        Raises:
            ValueError: If no table is found on the specified page.
        """
        tables = camelot.read_pdf(
            self.file_path,
            pages=str(page_number),
            **kwargs)

        if len(tables) > 0:
            return tables[0]
        else:
            raise ValueError(f"No table found in page n°{page_number}")
        
    def _convert_to_dataframe(self, table) -> pd.DataFrame:
        """
        Description:
            Converts a Camelot table object into a Pandas DataFrame.

        Args:
            table (camelot.core.Table): The Camelot table object to convert.

        Returns:
            pd.DataFrame: The DataFrame representation of the table.
        """
        return table.df


    @log_errors
    def _get_multiple_pages_table(self, starting_page_number: int, ending_page_number: int, **kwargs):
        """
        Description:
            Extracts tables from a range of pages in the PDF document and combines them into a single DataFrame.
            This method handles cases where tables span multiple pages in service company reports.

        Args:
            starting_page_number (int): The first page number to start extracting tables from.
            ending_page_number (int): The last page number to extract tables from.
            **kwargs: Additional keyword arguments to pass to Camelot's read_pdf function.

        Returns:
            pd.DataFrame: A combined DataFrame containing all extracted tables from the specified page range.

        Raises:
            ValueError: If no tables are found in the specified page range.
        """
        tables = []
        
        for page_number in range(starting_page_number, ending_page_number + 1):
            try:
                object_table = self._extract_single_page_table(page_number, **kwargs)
                table = self._convert_to_dataframe(object_table)
                tables.append(table)
            except ValueError:
                continue
            
        if not tables:
            raise ValueError("No table found in document") 
        
        final_table = pd.concat(tables, ignore_index=True)
        return final_table
    
    def _apply_formatting_pipeline(self, df: pd.DataFrame, cleaning_pipeline: list) -> pd.DataFrame:
        """
        Applies a sequence of cleaning functions to the DataFrame in the specified order.
        Each function in the pipeline transforms the DataFrame, allowing for modular and
        reusable data cleaning operations.

        Args:
            df (pd.DataFrame): The DataFrame to be cleaned.
            cleaning_pipeline (list): List of cleaning functions to apply sequentially.
                                      Each function should take and return a DataFrame.

        Returns:
            pd.DataFrame: The cleaned DataFrame after applying all pipeline functions.
        """
        cleaned_df = df.copy()
        for clean_func in cleaning_pipeline:
            cleaned_df = clean_func(cleaned_df)
        return cleaned_df

    def save_table_to_csv(self, table: pd.DataFrame, name: str, folder_path: str, header: bool = True):
        """
        Description:
            Saves a DataFrame to a CSV file in the specified folder. Creates the destination
            folder if it doesn't exist and logs the operation.

        Args:
            table (pd.DataFrame): The DataFrame to be saved.
            name (str): The name of the file (without extension).
            folder_path (str): The destination folder path.
            header (bool, optional): Whether to include column headers in the CSV file. Defaults to True.
        """
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{name}.csv")
        table.to_csv(file_path, header=header)
        logging.info(f"Table sauvegardée dans {file_path}")

    def visualize_camelot_parameters(self, page_number=0, **camelot_params):
        """
        Description:
            Visualizes the table extraction parameters on a specific PDF page using Camelot.
            This method helps debug and verify the accuracy of table extraction by displaying:
            - Column positions
            - Table areas
            - The extracted table structure

        Args:
            page_number (int): The page number to visualize (0-based index).
            **camelot_params: Camelot extraction parameters including:
                - columns: List of column positions as comma-separated string
                - table_areas: List of table area coordinates as comma-separated strings

        Returns:
            tuple: A tuple containing the matplotlib Figure and Axes objects for further customization.
        """

        table = self._extract_single_page_table(page_number, **camelot_params)
        
        plt.figure(figsize=(12, 16))
        camelot.plot(table, kind='contour')
        
        if 'columns' in camelot_params:
            columns = [float(x) for x in camelot_params['columns'][0].split(',')]
            for x in columns:
                plt.axvline(x=x, color='r', linestyle='--', label=f'Colonne {x}')

        if 'table_areas' in camelot_params:
            for area in camelot_params['table_areas']:
                x1, y1, x2, y2 = map(float, area.split(','))
                rect = plt.Rectangle((x1, y1), x2-x1, y2-y1,
                                   fill=False, color='m', linestyle='-',
                                   label='Zone de table')
                plt.gca().add_patch(rect)
        
        plt.title(f'Paramètres Camelot - Page {page_number}')
        plt.xlabel('X-coordinate')
        plt.ylabel('Y-coordinate')
        
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        return plt.gcf(), plt.gca()

    def standardize_columns(self, df):
        """
        Description:
            Standardizes DataFrame column names to a consistent format.
            Renames columns to: ['no', 'check_item', 'result'].

        Args:
            df (pd.DataFrame): The DataFrame whose columns need standardization.
                             Expected to have exactly 3 columns representing:
                             - Column 0: Item number/identifier
                             - Column 1: Description/check item
                             - Column 2: Result/status

        Returns:
            pd.DataFrame: The DataFrame with standardized column names.

        Raises:
            ValueError: If the input DataFrame doesn't have exactly 3 columns.
        """
        if len(df.columns) != 3:
            raise ValueError("Input DataFrame must have exactly 3 columns")
        df.columns = ['no', 'check_item', 'result']
        return df

    def merge_continuation_lines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Description:
            Merges continuation lines with their main lines in a DataFrame.
            A continuation line is identified by an empty first column.

        Args:
            df (pd.DataFrame): The DataFrame to clean. Continuation lines are identified
                            by an empty or whitespace-only first column.

        Returns:
            pd.DataFrame: The DataFrame with merged continuation lines.

        Process:
            1. Identifies continuation lines (empty first column)
            2. Merges content from continuation lines into the previous valid line
            3. Preserves content from subsequent columns of continuation lines
            4. Removes empty lines after merging
        """
        cleaned_df = df.copy()
        last_valid_idx = None
        
        for idx in cleaned_df.index:
            if pd.isna(cleaned_df.loc[idx, 0]) or str(cleaned_df.loc[idx, 0]).strip() == '':
                if last_valid_idx is not None:
                    if pd.notna(cleaned_df.loc[idx, 1]) and str(cleaned_df.loc[idx, 1]).strip():
                        cleaned_df.loc[last_valid_idx, 1] = (str(cleaned_df.loc[last_valid_idx, 1]) + ' ' + 
                                                           str(cleaned_df.loc[idx, 1])).strip()
                    
                    if (pd.isna(cleaned_df.loc[last_valid_idx, 2]) or 
                        cleaned_df.loc[last_valid_idx, 2].strip() == '') and pd.notna(cleaned_df.loc[idx, 2]):
                        cleaned_df.loc[last_valid_idx, 2] = cleaned_df.loc[idx, 2]
                    
                    cleaned_df.loc[idx, [1, 2]] = ''
            else:
                last_valid_idx = idx
                
        cleaned_df = cleaned_df[cleaned_df[1].str.strip() != '']
        
        return cleaned_df

    def _stack_columns_in_pairs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Description:
            Stacks DataFrame columns in pairs, renaming them to 0 and 1 respectively.
            Useful for processing tables with multiple columns that should be processed
            in pairs. For example, transforms:

            A  B  C  D  E  F

            Into:

            0  1
            A  B
            C  D
            E  F

        Args:
            df (pd.DataFrame): The DataFrame to process. Should have an even number
                            of columns for proper pairing.

        Returns:
            pd.DataFrame: A new DataFrame with columns stacked in pairs and renamed
                        to 0 and 1.
        """
        df_renamed = df.copy()
        df_renamed.columns = [i % 2 for i in range(len(df.columns))]
        
        stacked_pairs = []
        
        for i in range(0, len(df_renamed.columns), 2):
            pair = df_renamed.iloc[:, i:i+2]
            stacked_pairs.append(pair)
        
        result = pd.concat(stacked_pairs, ignore_index=True)
        
        return result

    def merge_rows_by_capitalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Description:
            Merges rows based on the capitalization of the first character.
            If a row's first character is not uppercase, it's considered a continuation
            of the previous row.

        Args:
            df (pd.DataFrame): The DataFrame to clean. Expected to have at least two columns:
                             - Column 0: Main content (used for capitalization check)
                             - Column 1: Additional information

        Returns:
            pd.DataFrame: The DataFrame with merged continuation rows.
        """
        cleaned_df = df.copy()
        last_valid_idx = None
        to_drop = []
        
        for idx in cleaned_df.index:
            if pd.notna(cleaned_df.loc[idx, 0]) and str(cleaned_df.loc[idx, 0]).strip():
                first_char = str(cleaned_df.loc[idx, 0]).strip()[0]
                if not first_char.isupper() and last_valid_idx is not None:
                    cleaned_df.loc[last_valid_idx, 0] = (str(cleaned_df.loc[last_valid_idx, 0]) + ' ' + 
                                                      str(cleaned_df.loc[idx, 0])).strip()
                    
                    if pd.notna(cleaned_df.loc[idx, 1]) and str(cleaned_df.loc[idx, 1]).strip():
                        if pd.isna(cleaned_df.loc[last_valid_idx, 1]) or not str(cleaned_df.loc[last_valid_idx, 1]).strip():
                            cleaned_df.loc[last_valid_idx, 1] = cleaned_df.loc[idx, 1]
                    
                    to_drop.append(idx)
                else:
                    last_valid_idx = idx
            
        cleaned_df = cleaned_df.drop(to_drop)
        
        return cleaned_df



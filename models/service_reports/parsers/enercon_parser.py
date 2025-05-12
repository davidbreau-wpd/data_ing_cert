import camelot, fitz, matplotlib.pyplot as plt, os, pandas as pd, re
from ..base import _Service_Report_Parser

class Enercon_PDF_Parser(_Service_Report_Parser):
    """
    Specialized class for processing Enercon service reports.
    Inherits from _Service_Report and adds Enercon-specific functionality.
    Handles the extraction and processing of inspection checklists
    from Enercon PDF reports.
    """
    def __init__(self, file_path):
        """Initialize an Enercon Report object.

        This class handles the processing and data extraction of Enercon service reports.
        It inherits from the _Service_Report base class and sets up specific parameters
        for parsing Enercon PDF documents.

        Args:
            file_path (str): Path to the PDF file to process
        """
        super().__init__(file_path)
        self._set_order_type()
        self._check_is_master()
        
        self.camelot_params = {
            'flavor': 'stream',
            'columns': ['65,450'],
            'table_areas': ['20,730,600,40'],
            'edge_tol': 700,
            'row_tol': 13,
            'split_text': False,   
            'strip_text': '\n',   
        }
    
    def _set_order_type(self):
        """
        Extract the order type from the first line of the first page.

        This method reads the first page of the PDF document and extracts the order type
        from its first line. The order type is typically found at the top of Enercon
        service reports and indicates the type of maintenance or inspection performed.

        The extracted order type is stored in the self.order_type attribute.

        Raises:
            Exception: If there is an error reading the PDF file or extracting the text.
            The error is caught and printed, and self.order_type is set to None.
        """
        try:
            with fitz.open(self.file_path) as doc:
                order_type = doc[0].get_text().split('\n')[0].strip()
                if order_type:
                    self.order_type = order_type
        except Exception as e:
            print(f"Erreur lors de l'extraction du type de commande: {e}")
            self.order_type = None
    
    def _check_is_master(self):
        """
        Determine if the report is of type MASTER or 4-YEARLY.
        
        This method checks if the extracted order type contains the keywords
        'MASTER' or 'YEARLY' to classify the report type.
        """
        try:
            self.is_master = bool(self.order_type and ("MASTER" in self.order_type or "YEARLY" in self.order_type))
        except Exception as e:
            print(f"Erreur lors de la détermination du type de rapport: {e}")
            self.is_master = False
    
    def _get_converter_master_data(self) -> pd.DataFrame:
        """
        Extracts the 'Converter Master Data' table from page 2 of the PDF report.

        This method retrieves and processes the converter master data table, which contains
        key technical information about the converter system. The table is extracted using
        specific parameters defined in master_data_params.

        Returns:
            pd.DataFrame: A processed DataFrame containing the converter master data with:
                - Technical parameters as index
                - Corresponding values in the 'Metadata' column
                - Empty rows removed
                - Columns stacked in pairs for better organization

        Note:
            The table extraction parameters are customized for this specific section:
            - Uses 3 columns at positions 125, 290, and 390
            - Targets the area between coordinates (20,700) and (600,620)
            - Enables text splitting for better data parsing
        """
        master_data_params = {
            **self.camelot_params,
            'columns': ['125, 290, 390'],
            'table_areas': ['20,700,600,620'],
            'split_text': True
        }
        
        master_data_table = self._extract_single_page_table(2, **master_data_params)
        master_data_df = self._convert_to_dataframe(master_data_table)
        merged_master_data_df = self._stack_columns_in_pairs(master_data_df)
        merged_master_data_df = merged_master_data_df.replace('', pd.NA).dropna(how='all')
        return merged_master_data_df
    
    def _get_details_on_order(self) -> pd.DataFrame:
        """
        Extracts the 'Details on Order' table from page 2 and merges continuation lines.

        This method retrieves and processes the 'Details on Order' table, which contains
        order-specific information. The table is extracted using customized parameters
        based on whether the report is a master/yearly report or not.

        The extraction parameters are adjusted to:
        - Use a single column at position 195
        - Target an area between coordinates that vary based on report type
        - Set row tolerance to 10 for merging nearby rows
        - Enable text splitting for better data parsing

        Returns:
            pd.DataFrame: A processed DataFrame containing the order details with:
                - Order information fields as rows
                - Merged continuation lines based on capitalization patterns
                - Empty rows removed
        """
        details_on_order_params = {
            **self.camelot_params,
            'columns': ['198'],
            'table_areas': [f'20,585,600,{380 if self.is_master else 430}'],
            'row_tol': 10,
            'split_text': True
        }
        
        details_table = self._extract_single_page_table(2, **details_on_order_params)
        details_on_order = self._convert_to_dataframe(details_table)
        
        details_on_order = self.merge_rows_by_capitalization(details_on_order)
        
        return details_on_order
    
    def _get_defects_summary(self) -> pd.DataFrame:
        """
        Extracts the defects summary table based on report type and reorganizes columns in pairs.

        This method retrieves and processes the defects summary table from page 2 of the report.
        The table extraction parameters are adjusted based on whether the report is a master/yearly
        report or not.

        The extraction parameters are customized to:
        - Use 5 columns at positions 115, 155, 235, 280, and 330
        - Target an area between coordinates that vary based on report type
        - Enable text splitting for better data parsing

        Returns:
            pd.DataFrame: A processed DataFrame containing the defects summary with:
                - Defect information organized in columns
                - Columns stacked in pairs for better organization
                - Empty rows removed
        """   
        table_areas = ['20, 265, 600, 300']
        
        defects_summary_params = {
            **self.camelot_params,
            'columns': ['115, 155, 235, 280, 330'],
            'table_areas': [f'20,{305 if self.is_master else 370},600,{275 if self.is_master else 340}'],
            'split_text': True
        }
        
        defects_summary_table = self._extract_single_page_table(2, **defects_summary_params)
        defects_summary_df = self._convert_to_dataframe(defects_summary_table)
        merged_defects_df = self._stack_columns_in_pairs(defects_summary_df)
        return merged_defects_df
    
    def get_metadata_df(self) -> pd.DataFrame:
        """
        Converts Enercon report metadata into a formatted DataFrame.

        This method combines three main data components from the report:
        - 'Converter Master Data': Technical specifications and parameters
        - 'Details on Order': Order-specific information
        - 'Defects Summary': Overview of identified defects

        Returns:
            pd.DataFrame: A formatted DataFrame containing:
                - Index: Field names from all three data components
                - Column 'Metadata': Corresponding values for each field
                - Empty rows and duplicate entries removed
                - Standardized formatting across all entries
        """
        converter_master_data = self._get_converter_master_data()
        details_on_order = self._get_details_on_order()
        defects_summary = self._get_defects_summary()
        
        metadata = pd.concat([converter_master_data, details_on_order, defects_summary], ignore_index=True)
        metadata = metadata[metadata[0].str.strip() != '']
        metadata.rename(columns={1: 'Metadata'}, inplace=True)
        metadata = metadata.set_index(0)
        metadata.index.name = None
        
        return metadata

    def extract_raw_checklist(self) -> pd.DataFrame:
        """
        Extract raw inspection checklist data from the PDF.
        """
        try:
            with fitz.open(self.file_path) as doc:
                total_pages = len(doc)

            tables = camelot.read_pdf(
                str(self.file_path),
                pages=f'2-{total_pages}',  # Changed from '3-end' to '2-{total_pages}'
                **self.camelot_params
            )
            
            return pd.concat([table.df for table in tables], ignore_index=True)
            
        except Exception as e:
            print(f"Error extracting raw checklist: {e}")
            return pd.DataFrame()

    def format_checklist(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format the raw inspection checklist data.
        
        This method:
        1. Extracts overview and checklist sections
        2. Applies formatting to each section
        3. Combines them into a final formatted DataFrame
        
        Args:
            df (pd.DataFrame): Raw checklist DataFrame
            
        Returns:
            pd.DataFrame: Formatted inspection checklist
        """
        overview_df = self._extract_report_overview(df, None)
        checklist_df = self._extract_inspection_checklist(df)
        return self._merge_dataframes(checklist_df, overview_df)

    def _filter_inspection_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This method extracts the relevant inspection data by:
        1. Finding the row after the 'Details' header
        2. Finding the row before the 'Signature' section
        3. Removing header rows with "No."
        """
        try:
            # Get start index (after "Details")
            start_idx = df[df[0].eq("Details")].index[0] + 1
            
            # Get end index (before "Signature")
            end_idx = df[df[0].str.contains("Signature", na=False)].index[0]
            
            # Filter rows between start and end, excluding "No." rows
            filtered_df = df.loc[start_idx:end_idx - 1]
            return filtered_df[~filtered_df[0].eq("No.")]
            
        except (IndexError, KeyError):
            return df

    def _check_and_get_overview(self, df: pd.DataFrame, camelot_tables) -> pd.DataFrame:
        """
        Check if Report Overview exists and extract it.
        Returns either the overview section or the complete df if no overview found.
        """
        overview_mask = df[0].str.contains("Report overview", na=False, case=False)
        if overview_mask.any():
            overview_index = overview_mask[overview_mask].index[0]
            # Keep only rows after "Report Overview"
            overview_df = self._extract_report_overview(df, camelot_tables)
            return overview_df if not overview_df.empty else df
        return df

    def format_table(self, df: pd.DataFrame, tables) -> pd.DataFrame:
        """Format the inspection table with minimal cleaning."""
        formatting_pipeline = [
            self._filter_inspection_rows,
            lambda x: self._check_and_get_overview(x, tables),
            super().standardize_columns,
            lambda x: self.merge_rows_by_capitalization(x, new_line=True)
        ]
        return super()._apply_formatting_pipeline(df, formatting_pipeline)

    def get_inspection_checklist_df(self) -> pd.DataFrame:
        """
        Extract and format the complete inspection checklist.
        """
        try:
            raw_checklist = self.extract_raw_checklist()
            return self.format_table(raw_checklist)
            
        except Exception as e:
            print(f"Error processing inspection checklist: {e}")
            return pd.DataFrame()

    def _extract_report_overview(self, df: pd.DataFrame, camelot_tables=None) -> pd.DataFrame:
        """Extract and format the Report Overview section"""
        try:
            # Find "Report Overview" row
            overview_row = df[df[0].str.contains("Report overview", na=False, case=False)].index[0]
            
            # Extract tables from page 3 onwards
            tables = camelot.read_pdf(
                str(self.file_path),
                pages='3-end',
                **self.camelot_params
            )
            
            # Find which table and page contains "Report Overview"
            row_count = 0
            for i, table in enumerate(tables):
                table_df = self._convert_to_dataframe(table)
                if row_count + len(table_df) > overview_row:
                    overview_page = i + 2  # +2 car camelot commence à la page 2
                    relative_row = overview_row - row_count
                    # Get y coordinate where to start extraction
                    y_coord = table.cells[relative_row][0].y1
                    break
                row_count += len(table_df)
            
            # Extract overview tables from multiple pages
            overview_dfs = []
            
            # First page: extract from Report Overview position
            first_params = {
                'flavor': 'stream',
                'columns': ['58,285,470'],
                'table_areas': [f'20,{y_coord},600,40'],
                'pages': str(overview_page),
                'edge_tol': 500,
                'row_tol': 10
            }
            first_table = camelot.read_pdf(self.file_path, **first_params)
            overview_dfs.extend(self._convert_to_dataframe(table) for table in first_table)
            
            # Following pages if needed
            if overview_page < len(tables) + 1:
                following_params = {
                    **self.camelot_params,
                    'columns': ['58,285,470'],
                    'pages': f"{overview_page + 1}-{len(tables) + 1}"
                }
                following_tables = camelot.read_pdf(self.file_path, **following_params)
                overview_dfs.extend(self._convert_to_dataframe(table) for table in following_tables)
            
            # Combine and clean
            overview_df = pd.concat(overview_dfs, ignore_index=True)
            return overview_df.dropna(how='all')
            
        except (IndexError, KeyError) as e:
            print(f"Error extracting report overview: {e}")
            return pd.DataFrame()
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

        Attributes:
            camelot_params (dict): Configuration parameters for Camelot table extraction:
                - flavor (str): Parser type ('stream')
                - columns (list): Column coordinates [65,450]
                - table_areas (list): Table boundary coordinates [20,730,600,40]
                - edge_tol (int): Edge tolerance for table detection (700)
                - row_tol (int): Row tolerance for merging (13)
                - split_text (bool): Whether to split text into multiple rows (False)
                - strip_text (str): Characters to strip from text ('\n')
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
        Extract the 'Details on Order' table from page 2 of the PDF report.
        
        Returns:
            pd.DataFrame: DataFrame containing the extracted details on order
        """
        details_params = {
            **self.camelot_params,
            'columns': ['125, 290, 390'],
            'table_areas': ['20,620,600,540'],
            'split_text': True
        }
        
        details_table = self._extract_single_page_table(2, **details_params)
        details_df = self._convert_to_dataframe(details_table)
        merged_details_df = self._stack_columns_in_pairs(details_df)
        merged_details_df = merged_details_df.replace('', pd.NA).dropna(how='all')
        return merged_details_df
    
    def _get_defects_summary(self) -> pd.DataFrame:
        """
        Extract the 'Defects Summary' table from page 2 of the PDF report.
        
        Returns:
            pd.DataFrame: DataFrame containing the extracted defects summary
        """
        defects_params = {
            **self.camelot_params,
            'columns': ['125, 290, 390'],
            'table_areas': ['20,540,600,460'],
            'split_text': True
        }
        
        defects_table = self._extract_single_page_table(2, **defects_params)
        defects_df = self._convert_to_dataframe(defects_table)
        merged_defects_df = self._stack_columns_in_pairs(defects_df)
        merged_defects_df = merged_defects_df.replace('', pd.NA).dropna(how='all')
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
        
        This method:
        1. Extracts tables from relevant pages
        2. Combines all tables into a single DataFrame
        
        Returns:
            pd.DataFrame: Raw inspection checklist data before formatting
        """
        try:
            tables = camelot.read_pdf(
                str(self.file_path),
                pages='3-end',
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

    def get_inspection_checklist_df(self) -> pd.DataFrame:
        """
        Extract and format the complete inspection checklist.
        
        This method:
        1. Extracts raw checklist data
        2. Applies formatting pipeline
        
        Returns:
            pd.DataFrame: Complete formatted inspection checklist
        """
        try:
            raw_checklist = self.extract_raw_checklist()
            return self.format_checklist(raw_checklist)
            
        except Exception as e:
            print(f"Error processing inspection checklist: {e}")
            return pd.DataFrame()
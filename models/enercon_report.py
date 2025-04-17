import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re
from .service_report import _Service_Report

class Enercon_Report(_Service_Report):
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
        Determines if the report is of type MASTER or 4-YEARLY.

        This method checks the order_type attribute to determine if the report
        is a MASTER or 4-YEARLY inspection report. These are special types of
        maintenance reports that require specific processing.

        The result is stored in the is_master attribute.
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
        
        return defects_summary_df 

    def get_metadata(self) -> pd.DataFrame:
        """
        Converts Enercon report metadata into a formatted DataFrame.

        This method combines three main data components from the report:
        - 'Converter Master Data': Technical specifications and parameters
        - 'Details on Order': Order-specific information
        - 'Defects Summary': Overview of identified defects

        The data is processed and merged into a single DataFrame with consistent formatting.

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
        
        self.metadata_df = metadata

        return metadata
    
    def set_metadata(self) -> pd.DataFrame:
        """
        Sets the metadata for the report by calling get_metadata() and stores it in metadata_df.

        This method retrieves the metadata using get_metadata() and assigns it to the
        metadata_df instance variable for later use.

        Returns:
            pd.DataFrame: A DataFrame containing the report metadata with:
                - Index: Field names from all data components
                - Column 'Metadata': Corresponding values for each field
                - Empty rows and duplicate entries removed
                - Standardized formatting across all entries
        """
        self.metadata_df = self.get_metadata()
        return self.metadata_df

    def extract_inspection_checklist(self) -> pd.DataFrame:
        """
        Extracts the raw inspection table from the Enercon report.

        This method retrieves the inspection checklist table from the PDF report using
        the default Camelot parameters defined in self.camelot_params.

        Returns:
            pd.DataFrame: Raw inspection table containing:
                - Inspection items and their details
                - Unprocessed data that requires further formatting
                - All pages of the inspection checklist combined
        """
        with fitz.open(self.file_path) as doc:
            total_pages = len(doc)
    
        inspection_params = {
            **self.camelot_params
        }
    
        return self._get_multiple_pages_table(
            starting_page_number=2,
            ending_page_number=total_pages,
            **inspection_params
        )

    def _filter_inspection_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This method extracts the relevant inspection data by:
        1. Finding the row after the 'Details' header
        2. Finding the row before the 'Signature' section
        3. Returning only rows between these boundaries

        Args:
            df (pd.DataFrame): Input DataFrame containing the inspection table

        Returns:
            pd.DataFrame: Filtered DataFrame containing only inspection data rows
        """
        # First get rows between Details and Signature
        filtered_df = df.loc[df[0].eq("Details").idxmax() + 1:df[0].str.contains("Signature", na=False).idxmax() - 1]
        
        # Then remove any remaining header rows
        return filtered_df[~filtered_df[0].eq("No.")]

    def format_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inspection table by applying the cleaning pipeline:
        1. Filtering relevant rows
        2. Standardizing column names

        Args:
            df (pd.DataFrame): Input DataFrame containing the raw inspection table

        Returns:
            pd.DataFrame: Formatted inspection table with filtered rows and standardized columns
        """
        formatting_pipeline = [
            self._filter_inspection_rows,
            super().standardize_columns
        ]
        
        formatted_table = super()._apply_formatting_pipeline(df, formatting_pipeline)
        
        return formatted_table

    def visualize_extraction_parameters(self, page_number: int, **kwargs):
        """
        Visualizes the extraction parameters configured for this report type.
        
        Args:
            page_number (int): Page number to visualize
            **kwargs: Camelot parameters to visualize
        """
        # Use provided parameters instead of self.camelot_params
        super().visualize_camelot_parameters(page_number, **kwargs)
        plt.show()

    def _set_filename(self) -> str:
        """
        Sets the filename based on metadata.
        
        Returns:
            str: Filename (without extension)
        """
        if not hasattr(self, 'metadata_df') or self.metadata_df is None:
            self.get_metadata()
            
        order_type = self.order_type if hasattr(self, 'order_type') and self.order_type else "unknown"
        order_number = self.metadata_df.loc["Order number", "Metadata"] if "Order number" in self.metadata_df.index else "unknown"
        serial_number = self.metadata_df.loc["Serial number", "Metadata"] if "Serial number" in self.metadata_df.index else "unknown"
        
        return f"{serial_number}_enercon_{order_type.replace(' ', '_').lower()}_{order_number}"

    def _process_report(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """Process and save report data.

        This method performs the complete processing pipeline for an Enercon report:
        1. Sets the order type and checks if it's a master/yearly report
        2. Extracts and formats metadata
        3. Extracts and formats the inspection checklist
        4. Saves both metadata and inspection data to CSV files

        Args:
            metadata_output_folder (str): Directory path where metadata CSV files will be saved
            inspection_checklist_output_folder (str): Directory path where inspection checklist CSV files will be saved

        The saved files will be named using the following pattern:
        - Metadata: 'metadata_<serial_number>_enercon_<order_type>_<order_number>.csv'
        - Inspection: 'inspection_<serial_number>_enercon_<order_type>_<order_number>.csv'
        """
        self._set_order_type()
        self._check_is_master()
        
        metadata = self.set_metadata()
        raw_inspection = self.extract_inspection_checklist()
        formatted_inspection = self.format_table(raw_inspection)
        
        filename = self._set_filename()
        
        self.save_table_to_csv(
            table=metadata,
            name=f"metadata_{filename}",
            folder_path=metadata_output_folder
        )
        
        self.save_table_to_csv(
            table=formatted_inspection,
            name=f"inspection_{filename}",
            folder_path=inspection_checklist_output_folder
        )

class Enercon_Reports_Processor:
    """
    Processor class to handle batch processing of Enercon reports
    """
    def __init__(self, input_folder: str):
        self.input_folder = input_folder

    def __call__(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """Process all Enercon PDF reports in a folder and save results to specified output locations.
        
        This method iterates through all PDF files in the input folder, processes each one
        using the Enercon_Report class, and saves the extracted data to the specified output
        locations.

        Args:
            metadata_output_folder (str): Directory path where metadata CSV files will be saved
            inspection_checklist_output_folder (str): Directory path where inspection checklist 
                CSV files will be saved

        The method will:
        1. Scan the input folder for PDF files
        2. Create an Enercon_Report object for each PDF
        3. Process each report to extract metadata and inspection checklists
        4. Save the extracted data as CSV files in the specified output folders

        Note:
            Only files with '.pdf' extension (case insensitive) will be processed.
            The output files will follow the naming convention defined in Enercon_Report._set_filename()
        """
        for pdf_file in os.listdir(self.input_folder):
            if pdf_file.lower().endswith('.pdf'):
                file_path = os.path.join(self.input_folder, pdf_file)
                report = Enercon_Report(file_path)
                report._process_report(
                    metadata_output_folder,
                    inspection_checklist_output_folder
                )


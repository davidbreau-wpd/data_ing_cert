import camelot, fitz, os, pandas as pd, re
from models import _Service_Report

class Vestas_Report(_Service_Report):
    """
    Specialized class for processing Vestas service reports.
    Inherits from _Service_Report and adds Vestas-specific functionality.
    Handles the extraction and processing of inspection checklists
    from Vestas PDF reports.
    """
    def __init__(self, file_path):
        """
        Initializes the Vestas report processor.

        Args:
            file_path (str): Path to the Vestas PDF report file.

        Attributes:
            metadata (dict): Extracted header information from the report
            metadata_df (pd.DataFrame): Metadata formatted as a DataFrame
            camelot_params (dict): Configuration parameters for table extraction
        """
        super().__init__(file_path)
        self.metadata = None
        self.metadata_df = None
        
        self.columns = [65, 330]
        self.camelot_params = {
            'flavor': 'stream',
            'edge_tol': 500,
            'row_tol': 10,
            'columns': [",".join(str(col) for col in self.columns)],
            'table_areas': ['30,740,600,100']
        }

    def get_metadata(self) -> dict:
        """
        Extracts header information from the first page of the report.

        Returns:
            dict: Contains key metadata like turbine number, service order, dates, etc.
        """
        first_page = super()._get_page(0)
        
        turbine_number = re.search(r'Turbine No\./Id:\s*(\d+)', first_page).group(1) if re.search(r'Turbine No\./Id:\s*(\d+)', first_page) else None
        service_order = re.search(r'Service Order:\s*(\d+)', first_page).group(1) if re.search(r'Service Order:\s*(\d+)', first_page) else None
        pad_no = (match.group(1).strip() if (match := re.search(r'PAD No\.\s*([^\n]+)', first_page)) else None)
        turbine_type = re.search(r'Turbine Type:\s*([\w\d]+)', first_page).group(1) if re.search(r'Turbine Type:\s*([\w\d]+)', first_page) else None
        start_date = re.search(r'Start Date:\s*([\d\.]+)', first_page).group(1) if re.search(r'Start Date:\s*([\d\.]+)', first_page) else None
        end_date = (match.group(1) if (match := re.search(r'End Date:\s*([\d\.]+)', first_page)) else None)
        date_and_time_of_receipt = (match.group(1).strip() if (match := re.search(r'Date & Time of Receipt\s*([\d\.\s:]+)', first_page)) else None)
        reason_for_call_out = (match.group(1) if (match := re.search(r'Reason for Call Out:\s*([^\n]+)', first_page)) else None)
                
        customer_address = ([line.strip() for line in match.group(1).split('\n') if line.strip()] 
                       if (match := re.search(r"Customer's Address:\s*(.*?)Site's Address:", first_page, re.DOTALL)) 
                       else None)
        
        return {
            'turbine_number': turbine_number,
            'service_order': service_order,
            'pad_no': pad_no,
            'turbine_type': turbine_type,
            'start_date': start_date,
            'end_date': end_date,
            'customer_address': customer_address,
            'date_and_time_of_receipt': date_and_time_of_receipt,
            'reason_for_call_out': reason_for_call_out
        }

    def set_metadata(self) -> pd.DataFrame:
        """
        Sets report metadata and converts it to DataFrame format.
        """
        self.metadata = self.get_metadata()
        self.metadata_df = pd.DataFrame([self.metadata]).T
        self.metadata_df.columns = ['Metadata']
        return self.metadata_df

    def _set_filename(self) -> str:
        """
        Generates filename based on metadata.

        Returns:
            str: Filename without extension
        """
        if self.metadata is None:
            self.set_metadata()
            
        # Clean filename by replacing spaces and special characters
        reason_for_call_out = str(self.metadata['reason_for_call_out']).replace(' ', '_').replace('/', '_')
        return f"{self.metadata['turbine_number']}_vestas_{self.metadata['service_order']}_{reason_for_call_out}"
    def extract_inspection_checklist(self) -> pd.DataFrame:
        """
        Extracts the inspection checklist table from the PDF report.

        This method:
        1. Locates the 'Service Inspection Form' page in the PDF
        2. Extracts tables from subsequent pages using camelot parameters
        3. Combines multi-page tables into a single DataFrame

        Returns:
            pd.DataFrame: The extracted inspection checklist table with raw data
                         before any formatting is applied

        Raises:
            ValueError: If no 'Service Inspection Form' page is found in the document
        """
        with fitz.open(self.file_path) as doc:
            # Find SIF page
            found_page = None
            for page_num in range(len(doc)):
                page_text = doc[page_num].get_text()
                if "Service Inspection Form" in page_text:
                    found_page = page_num
                    break
            
            if found_page is None:
                raise ValueError("No 'Service Inspection Form' page found in document")
                
            total_pages = len(doc)
    
        inspection_params = {
            **self.camelot_params,
            'split_text': True
        }
    
        return self._get_multiple_pages_table(
            starting_page_number=found_page + 1,
            ending_page_number=total_pages,
            **inspection_params
        )

    def _filter_inspection_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters inspection table rows starting from 'eSIF' marker.

        Args:
            df (pd.DataFrame): DataFrame containing inspection table data

        Returns:
            pd.DataFrame: Filtered DataFrame containing only rows from 'eSIF' marker onwards

        Note:
            If 'eSIF' marker is not found, returns the original DataFrame unchanged
        """
        try:
            start_idx = df[df[1].eq("eSIF")].index[0]
            return df.loc[start_idx:]
        except (IndexError, KeyError):
            return df

    def format_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format the inspection table by applying a series of cleaning operations.
        
        Args:
            df (pd.DataFrame): Raw inspection table data extracted from PDF
            
        Returns:
            pd.DataFrame: Cleaned and formatted inspection table with standardized columns
            
        The cleaning pipeline includes:
        - Filtering rows starting from 'eSIF' marker
        - Merging continuation lines
        - Standardizing column names and format
        """
        formatting_pipeline = [
            self._filter_inspection_rows,
            self.merge_continuation_lines,
            super().standardize_columns
        ]
        
        formatted_table = super()._apply_formatting_pipeline(df, formatting_pipeline)
        return formatted_table
       
    def _process_report(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """
        Process and save report data to specified output folders.

        This method:
        1. Extracts and saves metadata from the report
        2. Extracts and formats the inspection checklist
        3. Saves both datasets to their respective output locations

        Args:
            metadata_output_folder (str): Directory path where metadata CSV files will be saved
            inspection_checklist_output_folder (str): Directory path where inspection checklist CSV files will be saved

        The saved files will be named using the pattern:
        - Metadata: 'metadata_{turbine_number}_vestas_{service_order}_{reason_for_call_out}.csv'
        - Inspection: 'inspection_{turbine_number}_vestas_{service_order}_{reason_for_call_out}.csv'
        """
        # Get metadata
        metadata = self.set_metadata()
        
        # Extract and format data
        raw_inspection = self.extract_inspection_checklist()
        formatted_inspection = self.format_table(raw_inspection)
        
        filename = self._set_filename()
        
        # Save metadata and inspection tables
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

     

class Vestas_Reports_Processor:
    """
    Processor class to handle batch processing of Vestas reports
    """
    def __init__(self, input_folder: str):
        self.input_folder = input_folder

    def __call__(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """
        Process all Vestas PDF reports in a folder and save results to specified output locations.

        This method:
        1. Iterates through all PDF files in the input folder
        2. Creates a Vestas_Report instance for each file
        3. Processes each report to extract metadata and inspection checklists
        4. Saves the extracted data to the specified output folders

        Args:
            metadata_output_folder (str): Directory path where metadata CSV files will be saved
            inspection_checklist_output_folder (str): Directory path where inspection checklist CSV files will be saved

        The saved files will follow the naming pattern:
        - Metadata: 'metadata_{turbine_number}_vestas_{service_order}_{reason_for_call_out}.csv'
        - Inspection: 'inspection_{turbine_number}_vestas_{service_order}_{reason_for_call_out}.csv'
        """
        for pdf_file in os.listdir(self.input_folder):
            if pdf_file.lower().endswith('.pdf'):
                file_path = os.path.join(self.input_folder, pdf_file)
                report = Vestas_Report(file_path)
                report._process_report(
                    metadata_output_folder,
                    inspection_checklist_output_folder
                )
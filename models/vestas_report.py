import camelot, fitz, pandas as pd
from .service_report import _Service_Report

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
        
        self.columns = [65, 330, 350]
        self.camelot_params = {
            'flavor': 'stream',
            'edge_tol': 500,
            'row_tol': 10,
            'columns': [",".join(str(col) for col in self.columns)]
        }

    def get_header_informations(self) -> dict:
        """
        Extracts header information from the first page of the report.

        Returns:
            dict: Contains key metadata like turbine number, service order, dates, etc.
        """
        # TODO: Implement header information extraction
        return {
            'turbine_number': '',
            'service_order': '',
            'reason_for_call_out': '',
            # Add other metadata fields
        }

    def set_metadata(self) -> pd.DataFrame:
        """
        Sets report metadata and converts it to DataFrame format.
        """
        self.metadata = self.get_header_informations()
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
            
        return f"{self.metadata['turbine_number']}_vestas_{self.metadata['service_order']}_{self.metadata['reason_for_call_out']}"

    def _process_report(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """Process and save report data"""
        # Extract and format data
        raw_inspection = self.extract_inspection_checklist()
        formatted_inspection = self._filter_inspection_rows(raw_inspection)
        
        # Save metadata
        self.save_metadata(metadata_output_folder)
        
        # Save inspection data
        self.save_inspection_data(formatted_inspection, inspection_checklist_output_folder)

    def save_metadata(self, folder_path: str):
        """
        Saves metadata to CSV file.
        """
        if self.metadata_df is None:
            self.set_metadata()
            
        filename = self._set_filename()
        self.save_table_to_csv(
            table=self.metadata_df,
            name=f"metadata_{filename}",
            folder_path=folder_path
        )

    def save_inspection_data(self, table: pd.DataFrame, folder_path: str):
        """
        Saves inspection data to CSV file.
        """
        filename = self._set_filename()
        self.save_table_to_csv(
            table=table,
            name=filename,
            folder_path=folder_path
        )

    def _set_order_type(self):
        """
        Extrait le type de commande depuis la première ligne de la première page.
        """
        try:
            with fitz.open(self.file_path) as doc:
                self.order_type = doc[0].get_text().split('\n')[0].strip()
        except Exception as e:
            print(f"Erreur lors de l'extraction du type de commande: {e}")
            self.order_type = None

    def extract_inspection_checklist(self) -> pd.DataFrame:
        """
        Extrait la table d'inspection brute du rapport Vestas.
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
        Filtre les lignes de la table entre Inspection et Signature.
        """
        return df.loc[df[0].eq("Inspection").idxmax() + 1:df[0].str.contains("Signature", na=False).idxmax() - 1]

    def _process_report(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """Process and save report data"""
        # Extract and format data
        raw_inspection = self.extract_inspection_checklist()
        formatted_inspection = self._filter_inspection_rows(raw_inspection)
        
        # Save inspection table
        self.save_table_to_csv(
            table=formatted_inspection,
            name=f"inspection_{self.order_type.lower().replace(' ', '_')}",
            folder_path=inspection_checklist_output_folder
        )
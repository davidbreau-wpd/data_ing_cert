import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re
from .service_report import _Service_Report
from .utils import log_errors, dataframe_required

class Vestas_Report(_Service_Report):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.metadata = None
        self.metadata_df = None
        
        self.camelot_params = {
            'flavor': 'stream',
            'columns': ['65,330'],
            'table_areas': ['30,730,600,100'],
            'edge_tol': 700,
            'row_tol': 13,
            'split_text': True,   # Pour gérer le texte qui traverse les colonnes
            'strip_text': '\n',   # Pour nettoyer le texte des retours à la ligne
        }
        
    def _find_starting_page(self) -> int:
        """
        Trouve la page de départ pour un rapport Vestas.
        
        Returns:
            int: Numéro de la page contenant "Service Inspection Form"
            
        Raises:
            ValueError: Si aucune page correspondante n'est trouvée
        """
        with fitz.open(self.file_path) as doc:
            for page_num in range(len(doc)):
                if "Service Inspection Form" in doc[page_num].get_text():
                    break
            else:  # This else clause executes if no break occurred in the for loop
                raise ValueError("No 'Service Inspection Form' page found in document")
            return page_num

    def _set_filename(self) -> str:
        """
        Définit le nom de fichier basé sur les métadonnées.
        
        Returns:
            str: Nom du fichier (sans extension)
        """
        if self.metadata is None:
            self.get_metadata()
            
        # Clean reason_for_call_out for filename
        reason = self.metadata['reason_for_call_out'] or "unknown"
        reason = re.sub(r'[^\w\s-]', '', reason)[:30].strip().replace(' ', '_')
            
        return f"{self.metadata['turbine_number']}_vestas_{self.metadata['service_order']}_{reason}"

    def __call__(self, metadata_output_folder: str, inspection_checklist_output_folder: str, input_folder: str):
        """
        Process one or multiple reports and save results.
        
        Args:
            metadata_output_folder: Where to save metadata CSVs
            inspection_checklist_output_folder: Where to save inspection CSVs
            input_folder: Folder containing PDF(s) to process
            
        Raises:
            FileNotFoundError: If any of the folders doesn't exist
        """
        # Validate folders
        for folder in [input_folder, metadata_output_folder, inspection_checklist_output_folder]:
            os.makedirs(folder, exist_ok=True)
                
        # Process PDFs
        try:
            for pdf_file in os.listdir(input_folder):
                if pdf_file.lower().endswith('.pdf'):
                    self.file_path = os.path.join(input_folder, pdf_file)
                    self._process_report(
                        os.path.join(metadata_output_folder),
                        os.path.join(inspection_checklist_output_folder)
                    )
        except (PermissionError, FileNotFoundError) as e:
            logging.error(f"Error accessing directory {input_folder}: {str(e)}")

    # Ces méthodes peuvent être supprimées car remplacées par _process_report
    # def save_metadata(self, metadata_df: pd.DataFrame, folder_path: str):
    # def save_inspection_data(self, table: pd.DataFrame, folder_path: str):
import camelot, fitz, pandas as pd
from .service_report import _Service_Report

class Vestas_Report(_Service_Report):
    def __init__(self, file_path):
        super().__init__(file_path)
        self._set_order_type()
        
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
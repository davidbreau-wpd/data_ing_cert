import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re
from .service_report import _Service_Report

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
        self._open()
        found_page = None
        for page_num in range(len(self.doc)):
            page_text = self.doc[page_num].get_text()
            if "Service Inspection Form" in page_text:
                found_page = page_num
                break
        self._close()
        
        if found_page is not None:
            return found_page
        raise ValueError("No 'Service Inspection Form' page found in document")
        
    def get_header_informations(self):
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
        
        header_informations = {
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
        
        return header_informations
    
    def _extract_full_table(self, columns=None) -> pd.DataFrame:
        starting_page = self._find_starting_page() + 1
        self._open()
        ending_page = len(self.doc)
        self._close()
        
        params = self.camelot_params.copy()
        if columns is not None:
            params['columns'] = [",".join(str(col) for col in columns)]
            
        return self._get_multiple_pages_table(
            starting_page_number=starting_page,
            ending_page_number=ending_page,
            **params
        )
        
    def visualize_extraction_parameters(self, page_number: int):
        """
        Visualise les paramètres d'extraction configurés pour ce type de rapport.
        
        Args:
            page_number (int): Numéro de la page à visualiser
        """
        super().visualize_camelot_parameters(page_number, **self.camelot_params)
        plt.show()
        
        
    def format_table(self, df):
        """
        Formats the raw inspection table by:
        1. Merging continuation lines
        2. Standardizing column names
        
        Args:
            df (pd.DataFrame): Raw DataFrame extracted from PDF
            
        Returns:
            pd.DataFrame: Formatted DataFrame with standardized columns
        """
        # Merge continuation lines
        merged_df = self.merge_continuation_lines(df)
        
        # Standardize column names
        formatted_df = super().standardize_columns(merged_df)
        
        return formatted_df
        
    def set_metadata(self) -> pd.DataFrame:
        """
        Définit les métadonnées du rapport et les convertit en DataFrame.
        """
        self.metadata = self.get_header_informations()
        self.metadata_df = pd.DataFrame([self.metadata]).T
        self.metadata_df.columns = ['Metadata']
        return self.metadata_df

    def _set_filename(self) -> str:
        """
        Définit le nom de fichier basé sur les métadonnées.
        
        Returns:
            str: Nom du fichier (sans extension)
        """
        if self.metadata is None:
            self.set_metadata()
            
        return f"{self.metadata['turbine_number']}_vestas_{self.metadata['service_order']}_{self.metadata['reason_for_call_out']}"

    def save_metadata(self, folder_path: str):
        """
        Sauvegarde les métadonnées dans un fichier CSV.
        
        Args:
            folder_path: Chemin du dossier de destination
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
        Sauvegarde les données d'inspection.
        """
        filename = self._set_filename()
        
        self.save_table_to_csv(
            table=table,
            name=filename,
            folder_path=folder_path
        )
        

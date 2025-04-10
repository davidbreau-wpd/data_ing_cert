import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re
from .service_report import _Service_Report

class Enercon_Report(_Service_Report):
    def __init__(self, file_path):
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
        Extrait le type de commande depuis la première ligne de la première page.
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
        Détermine si le rapport est de type MASTER ou 4-YEARLY.
        """
        try:
            self.is_master = bool(self.order_type and ("MASTER" in self.order_type or "YEARLY" in self.order_type))
        except Exception as e:
            print(f"Erreur lors de la détermination du type de rapport: {e}")
            self.is_master = False


    def _get_converter_master_data(self) -> pd.DataFrame:
        """
        Extrait la table 'Converter Master Data' de la page 2.
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
        Extrait la table 'Details on Order' de la page 2 et fusionne les lignes de continuation.
        """
        details_on_order_params = {
            **self.camelot_params,
            'columns': ['195'],
            'table_areas': [f'20,590,600,{380 if self.is_master else 420}'],
            'row_tol': 10,
            'split_text': True
        }
        
        details_table = self._extract_single_page_table(2, **details_on_order_params)
        details_on_order = self._convert_to_dataframe(details_table)
        
        details_on_order = self.merge_rows_by_capitalization(details_on_order)
        
        return details_on_order

    def _get_defects_summary(self) -> pd.DataFrame:
        """
        Extrait la table des défauts selon le type de rapport et réorganise les colonnes par paires.
        """
        defects_summary_params = {
            **self.camelot_params,
            'columns': ['115, 155, 235, 280, 330'],
            'table_areas': [f'20,{370 if not self.is_master else 265},600,{330 if not self.is_master else 305}'],
            'split_text': True
        }
        
        defects_summary_table = self._extract_single_page_table(2, **defects_summary_params)
        defects_summary_df = self._convert_to_dataframe(defects_summary_table)
        merged_defects_df = self._stack_columns_in_pairs(defects_summary_df)
        return merged_defects_df
        
        return defects_summary_df 

    def get_metadata(self) -> pd.DataFrame:
        """
        Convertit les métadonnées du rapport Enercon en DataFrame formaté.
        Combine 'Converter Master Data', 'Details on Order', et 'Defects Summary'.
        
        Returns:
            pd.DataFrame: DataFrame avec une colonne 'Metadata' et les noms des champs en index
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

    def extract_inspection_checklist(self) -> pd.DataFrame:
        """
        Extrait la table d'inspection brute du rapport Enercon.
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
        Filtre les lignes de la table entre Details et Signature.
        """
        return df.loc[df[0].eq("Details").idxmax() + 1:df[0].str.contains("Signature", na=False).idxmax() - 1]

    def format_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formate la table d'inspection en appliquant le pipeline de nettoyage :
        1. Filtrant les lignes pertinentes
        2. Standardisant les noms de colonnes
        """
        formatting_pipeline = [
            self._filter_inspection_rows,
            super().standardize_columns
        ]
        
        formatted_table = super()._apply_formatting_pipeline(df, formatting_pipeline)
        
        return formatted_table

    def visualize_extraction_parameters(self, page_number: int):
        """
        Visualise les paramètres d'extraction configurés pour ce type de rapport.
        
        Args:
            page_number (int): Numéro de la page à visualiser
        """
        super().visualize_camelot_parameters(page_number, **self.camelot_params)
        plt.show()

    def _set_filename(self) -> str:
        """
        Définit le nom de fichier basé sur les métadonnées.
        
        Returns:
            str: Nom du fichier (sans extension)
        """
        if not hasattr(self, 'metadata_df') or self.metadata_df is None:
            self.get_metadata()
            
        order_type = self.order_type if hasattr(self, 'order_type') and self.order_type else "unknown"
        order_number = self.metadata_df.loc["Order number", "Metadata"] if "Order number" in self.metadata_df.index else "unknown"
        serial_number = self.metadata_df.loc["Serial number", "Metadata"] if "Serial number" in self.metadata_df.index else "unknown"
        
        return f"{serial_number}_enercon_{order_type.replace(' ', '_').lower()}_{order_number}"

    def _process_report(self, metadata_output_folder: str, inspection_checklist_output_folder: str):
        """Process and save report data"""
        metadata = self.get_metadata()
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

    def __call__(self, input_folder: str = None, metadata_output_folder: str = None, inspection_checklist_output_folder: str = None):
        """
        Process one or multiple reports and save results.
        
        Args:
            metadata_output_folder: Where to save metadata CSVs
            inspection_checklist_output_folder: Where to save inspection CSVs
            input_folder: Optional folder containing multiple PDFs to process
        """
        if input_folder:
            for pdf_file in os.listdir(input_folder):
                if pdf_file.lower().endswith('.pdf'):
                    self.file_path = os.path.join(input_folder, pdf_file)
                    self._set_order_type()
                    self._check_is_master()
                    self._process_report(metadata_output_folder, inspection_checklist_output_folder)
        else:
            self._process_report(metadata_output_folder, inspection_checklist_output_folder)
    
    
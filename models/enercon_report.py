import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re
from .service_report import _Service_Report

class Enercon_Report(_Service_Report):
    def __init__(self, file_path):
        super().__init__(file_path)
        
        self.camelot_params = {
            'flavor': 'stream',
            'columns': ['65,450'],
            'table_areas': ['20,730,600,40'],
            'edge_tol': 700,
            'row_tol': 13,
            'split_text': False,   
            'strip_text': '\n',   
        }

    def _get_converter_master_data(self) -> pd.DataFrame:
        """
        Extrait la table 'Converter Master Data' de la page 2.
        Réorganise les colonnes pour regrouper les données :
        A B C D    ->    A B
        E F G H    ->    E F
        I J            I J
                        C D
                        G H
        """
        master_params = self.camelot_params.copy()
        master_params.update({
            'columns': ['130, 290, 390'],
            'table_areas': ['20,700,600,620'],
        })
        
        master_table = self._extract_single_page_table(2, **master_params)
        master_df = self._convert_to_dataframe(master_table)
        
        # Séparer les deux groupes de colonnes
        first_group = master_df[[0, 1]]
        second_group = master_df[[2, 3]]
        
        # Renommer les colonnes du second groupe pour éviter les conflits
        second_group.columns = [0, 1]
        
        # Concaténer les deux groupes verticalement
        converter_master_data = pd.concat([first_group, second_group], ignore_index=True)
        
        # Nettoyer les lignes vides (avec dropna) et celles ne contenant que des espaces
        converter_master_data = converter_master_data.dropna(how='all')
        converter_master_data = converter_master_data[
            converter_master_data.apply(lambda x: x.str.strip().str.len() > 0).any(axis=1)
        ]
        
        return converter_master_data

    def _get_details_on_order(self) -> pd.DataFrame:
        """
        Extrait la table 'Details on Order' de la page 2.
        """
        details_params = self.camelot_params.copy()
        details_params.update({
            'columns': ['195'],
            'table_areas': ['20,590,600,420'],
        })
        
        details_table = self._extract_single_page_table(2, **details_params)
        details_on_order = self._convert_to_dataframe(details_table)
        
        return details_on_order

    def get_metadata(self) -> pd.DataFrame:
        """
        Convertit les métadonnées du rapport Enercon en DataFrame formaté.
        Combine 'Converter Master Data' et 'Details on Order'.
        
        Returns:
            pd.DataFrame: DataFrame avec une colonne 'Metadata' et les noms des champs en index
        """
        # Récupérer les deux tables
        converter_master_data = self._get_converter_master_data()
        details_on_order = self._get_details_on_order()
        
        # Concaténer les deux DataFrames
        metadata = pd.concat([converter_master_data, details_on_order], ignore_index=True)
        
        # Nettoyer les données (supprimer les lignes vides)
        metadata = metadata[metadata[0].str.strip() != '']
        
        metadata.rename(columns={1: 'Metadata'}, inplace=True)
        metadata = metadata.set_index(0)
        metadata.index.name = None

        return metadata

    def extract_inspection_table(self) -> pd.DataFrame:
        """
        Extrait la table d'inspection du rapport Enercon.
        Commence à la page 2 et continue jusqu'à la fin du document.
        
        Returns:
            pd.DataFrame: Table d'inspection brute
        """
        # Ouvrir le document pour obtenir le nombre total de pages
        self._open()
        last_page = len(self.doc)
        self._close()
        
        # Extraire la table de toutes les pages à partir de la page 2
        inspection_table = self._get_multiple_pages_table(
            starting_page_number=2,
            ending_page_number=last_page,
            **self.camelot_params
        )
        
        return inspection_table
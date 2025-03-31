import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re, numpy as np

class _Service_Report:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _open(self):
        self.doc = fitz.open(self.file_path)
        
    def _close(self):
        if self.doc is not None:
            self.doc.close()
            self.doc = None

    def _get_page(self, page_number: int) -> str:
        self._open()
        page = self.doc[page_number].get_text()
        self._close()
        return page

    def _extract_single_page_table(self, page_number: int, **kwargs) -> camelot.core.Table:
        tables = camelot.read_pdf(
            self.file_path,
            pages=str(page_number),
            **kwargs)

        if len(tables) > 0:
            return tables[0]
        else:
            raise ValueError(f"No table found in page n°{page_number}")
        
    def _convert_to_dataframe(self, table) -> pd.DataFrame:
        return table.df


    def plot_column_lines(self, table: camelot.core.Table, columns: list, title:str=None, kind='contour'):
        plt.figure()
        camelot.plot(table, kind=kind)
        for col in columns:
            plt.axvline(x=col, color='r', linestyle='--', label=f'Column {col}')
        plt.title(title)
        plt.xlabel('X-coordinate')
        plt.ylabel('Y-coordinate')
        plt.legend()
        plt.show()


    def _get_multiple_pages_table(self, starting_page_number: int, ending_page_number: int, **kwargs):
        tables = []
        
        for page_number in range(starting_page_number, ending_page_number + 1):
            try:
                object_table = self._extract_single_page_table(page_number, **kwargs)
                table = self._convert_to_dataframe(object_table)
                tables.append(table)
            except ValueError:
                continue
            
        if not tables:
            raise ValueError("No table found in document") 
        
        final_table = pd.concat(tables, ignore_index=True)
        return final_table
    
    def _clean_table(self, df: pd.DataFrame, cleaning_pipeline: list) -> pd.DataFrame:
        """
        Applique une séquence de fonctions de nettoyage au DataFrame.
        
        Args:
            df: DataFrame à nettoyer
            cleaning_pipeline: Liste de fonctions de nettoyage à appliquer
        """
        cleaned_df = df.copy()
        for clean_func in cleaning_pipeline:
            cleaned_df = clean_func(cleaned_df)
        return cleaned_df

    def save_table_to_csv(self, table: pd.DataFrame, name: str, folder_path: str, header: bool = True):
        """
        Sauvegarde une table en CSV.
        
        Args:
            table: DataFrame à sauvegarder
            name: Nom du fichier (sans extension)
            folder_path: Chemin du dossier de destination
            header: Si True, écrit l'en-tête des colonnes
        """
        file_path = os.path.join(folder_path, f"{name}.csv")
        table.to_csv(file_path, header=header)

    def visualize_camelot_parameters(self, page_number=0, **camelot_params):
        """
        Visualise graphiquement les paramètres Camelot sur une page donnée.
        
        Args:
            page_number (int): Numéro de la page à visualiser
            **camelot_params: Paramètres Camelot (columns, table_areas, etc.)
        """
        # Extraire une table temporaire pour avoir la visualisation de base
        table = self._extract_single_page_table(page_number, **camelot_params)
        
        plt.figure(figsize=(12, 16))
        camelot.plot(table, kind='contour')
        
        # Tracer les lignes de colonnes si spécifiées
        if 'columns' in camelot_params:
            columns = [float(x) for x in camelot_params['columns'][0].split(',')]
            for x in columns:
                plt.axvline(x=x, color='r', linestyle='--', label=f'Colonne {x}')
        
        # Tracer les zones de table si spécifiées
        if 'table_areas' in camelot_params:
            for area in camelot_params['table_areas']:
                x1, y1, x2, y2 = map(float, area.split(','))
                rect = plt.Rectangle((x1, y1), x2-x1, y2-y1,
                                   fill=False, color='m', linestyle='-',
                                   label='Zone de table')
                plt.gca().add_patch(rect)
        
        plt.title(f'Paramètres Camelot - Page {page_number}')
        plt.xlabel('X-coordinate')
        plt.ylabel('Y-coordinate')
        
        # Dédupliquer la légende
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        return plt.gcf(), plt.gca()

    def standardize_columns(self, df):
        """Standardise les noms de colonnes"""
        df.columns = ['item_number', 'inspection_detail', 'status']
        return df

    def merge_continuation_lines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fusionne les lignes de continuation avec leurs lignes principales.
        Une ligne de continuation est identifiée par une première colonne vide.
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            pd.DataFrame: DataFrame avec les lignes fusionnées
        """
        cleaned_df = df.copy()
        last_valid_idx = None
        
        for idx in cleaned_df.index:
            # Si la première colonne est vide, c'est une ligne de continuation
            if pd.isna(cleaned_df.loc[idx, 0]) or str(cleaned_df.loc[idx, 0]).strip() == '':
                if last_valid_idx is not None:
                    # Fusionner le texte de la colonne 1
                    if pd.notna(cleaned_df.loc[idx, 1]) and str(cleaned_df.loc[idx, 1]).strip():
                        cleaned_df.loc[last_valid_idx, 1] = (str(cleaned_df.loc[last_valid_idx, 1]) + ' ' + 
                                                           str(cleaned_df.loc[idx, 1])).strip()
                    
                    # Conserver le statut de la colonne 2 s'il n'existe pas déjà
                    if (pd.isna(cleaned_df.loc[last_valid_idx, 2]) or 
                        cleaned_df.loc[last_valid_idx, 2].strip() == '') and pd.notna(cleaned_df.loc[idx, 2]):
                        cleaned_df.loc[last_valid_idx, 2] = cleaned_df.loc[idx, 2]
                    
                    # Vider la ligne de continuation
                    cleaned_df.loc[idx, [1, 2]] = ''
            else:
                last_valid_idx = idx
                
        # Supprimer les lignes vides après fusion
        cleaned_df = cleaned_df[cleaned_df[1].str.strip() != '']
        
        return cleaned_df



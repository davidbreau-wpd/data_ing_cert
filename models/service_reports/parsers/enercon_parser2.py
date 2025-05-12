import camelot
import fitz
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
from ..base import _Service_Report_Parser

class Enercon_PDF_Parser(_Service_Report_Parser):
    """ Summerize:
    Specialized class for processing Enercon service reports.
    Inherits from _Service_Report and adds Enercon-specific functionality.
    Handles the extraction and processing of inspection checklists
    from Enercon PDF reports.
    """
    def __init__(self, file_path):
        """Initialize an Enercon Report object.

        Args:
            file_path (str): Path to the PDF file to process
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
        
    def _set_order_type(self) -> None:
        """ Extract the order type from the first line of the first page.
    Raises:
        Exception: If there is an error reading the PDF file or extracting the text
        """
        try:
            with fitz.open(self.file_path) as doc:
                order_type = doc[0].get_text().split('\n')[0].strip()
                if order_type:
                    self.order_type = order_type
        except Exception as e:
            print(f"Erreur lors de l'extraction du type de commande: {e}")
            self.order_type = None
            
    def _check_is_master(self) -> None:
        """ Determines if the report is of type MASTER or 4-YEARLY by checking what's in self.order_type anticipating the bonus rows master type report have
    Attributes:
        is_master(Bool) : True if order_type is either one of them
        """
        try:
            self.is_master = bool(self.order_type and ("MASTER" in self.order_type or "YEARLY" in self.order_type))
        except Exception as e:
            print(f"Error determining report type: {e}")
            self.is_master = False
            
    def _set_converter_master_data(self) -> None:
        """Extract and process converter master data from page 2 of the report.
        Attributes:
            master_data(pd.DataFrame): Processed converter master data
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
        adjusted_merged_master_data_df.replace('', pd.NA).dropna(how='all')
            #Extracts from table2 / uses pandas / adjust columns / drop empty cells
            
        self.master_data = adjusted_merged_master_data_df
        


    def _set_details_on_order(self) -> None:
        """ Extracts the 'Details on Order' table from page 2 and merges continuation lines.
        Attributes:
            details_on_order_df(pd.DataFrame): A processed DataFrame containing the order details
        """
        details_on_order_params = {
            **self.camelot_params,
            'columns': ['198'],
            'table_areas': [f'20,585,600,{380 if self.is_master else 430}'],
            'row_tol': 10,
            'split_text': True
        }
        
        details_table = self._extract_single_page_table(2, **details_on_order_params)
        details_on_order_df = self._convert_to_dataframe(details_table)
        merged_details_on_order_df = self.merge_rows_by_capitalization(details_on_order_df)
            # extracts table / convert to pandas format / fuse cells
            
        self.details_on_order = merged_details_on_order_df
        
    def _set_defects_summary(self) -> pd.DataFrame:
        """ Extracts the defects summary table based on report type and reorganizes columns in pairs.
        Note:
            The table extraction parameters are adjusted based on whether the report is a master/yearly report or not.
        Attributes:
            defects_summary(pd.DataFrame): A processed DataFrame containing the defects summary
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


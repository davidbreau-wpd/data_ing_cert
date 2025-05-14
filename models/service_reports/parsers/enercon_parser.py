import camelot
import fitz
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
from typing import List

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
        adjusted_merged_master_data_df = merged_master_data_df.replace('', pd.NA).dropna(how='all')
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
        
    def _set_defects_summary(self) -> None:
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
            # sets parameters / extract camelot table / convert in pandas df / adjust columns
        
        self.defects_summary = merged_defects_df

    def _set_metadata_df(self) -> None:
        """ Converts Enercon report metadata into a formatted DataFrame.
        Attributes:
            metadata(pd.DataFrame): A formatted DataFrame containing report's metadata
        """
        self._set_converter_master_data()
        self._set_details_on_order()
        self._set_defects_summary()
        metadata = pd.concat([self.master_data, self.details_on_order, self.defects_summary], ignore_index=True)
        metadata = metadata[metadata[0].str.strip() != '']
        metadata.rename(columns={1: 'Metadata'}, inplace=True)
        metadata = metadata.set_index(0)
        metadata.index.name = None
            # extract 3 parts of header metadatas / concatenate them / adjust df
            
        self.metadata = metadata

    def _set_inspection_checklist(self) -> None:
        """ Extract and format the complete inspection checklist.
        Attributes:
            inspection_checklist(pd.DataFrame): Formatted inspection checklist
        """
        self.extract_raw_checklist()
        self.format_checklist()

        
    def extract_raw_checklist(self) -> pd.DataFrame:
        """ Extract raw inspection checklist data from the PDF.
        
        Attributes:
            camelot_tables(List[camelot.core.Table]): List of extracted Camelot table objects
            raw_checklist(pd.DataFrame): DataFrame containing inspection checklist | empty dataframe on error
        """
        try:
            with fitz.open(self.file_path) as doc:
                total_pages = len(doc)
            tables = camelot.read_pdf(
                str(self.file_path),
                pages=f'2-{total_pages}',
                **self.camelot_params
            )
            concatenated_tables = pd.concat([table.df for table in tables], ignore_index=True)
                #count pages / extracts tables / concatenate them in pandas df
            
            self.camelot_tables = tables
            self.raw_checklist = concatenated_tables
            
        except Exception as e:
            logging.error(f"Error extracting raw checklist: {e}")
            self.camelot_tables = list()
            self.raw_checklist = pd.DataFrame()

    def _has_report_overview(self) -> None:
        """ Check if Report Overview exists anywhere in the first column of report.
        
        Attributes:
            has_report_overview(Bool): True if Report Overview is in report | False
        """
        raw_checklists_first_column = self.raw_checklist[0]
        overview_mask = raw_checklists_first_column.str.contains("Report overview", na=False, case=False)
        self.has_report_overview = overview_mask.any() 
            
    def _get_report_overview(self) -> None:
        """ Extract Report Overview section if it exists.
        Attributes:
            overview_df(pd.DataFrame): Overview section of the report | empty DataFrame if no overview 
        """        
        if not self.has_report_overview:
            self.overview_df = pd.DataFrame()
            return
            
        # Find where overview starts
        overview_mask = self.raw_checklist[0].str.contains("Report overview", na=False, case=False)
        if not overview_mask.any():
            self.overview_df = pd.DataFrame()
            return
            
        # Get the overview section
        overview_start_index = overview_mask[overview_mask].index[0]
        self.overview_df = self.raw_checklist.iloc[overview_start_index + 1:].reset_index(drop=True)

    def process_report_overview(self) -> None:
        """ Process the Report Overview section """
        self._has_report_overview()
        self._get_report_overview()
        
        if not self.overview_df.empty:
            # Get main checklist part (before overview)
            overview_mask = self.raw_checklist[0].str.contains("Report overview", na=False, case=False)
            overview_start = overview_mask[overview_mask].index[0]
            self.preprocessed_checklist = self.raw_checklist.iloc[:overview_start].reset_index(drop=True)
            
            # Merge with overview
            self.preprocessed_checklist = super()._merge_dataframes(
                self.preprocessed_checklist,
                self.overview_df,
                columns_to_keep=[0, 1, 2]
            )
        else:
            self.preprocessed_checklist = self.raw_checklist.reset_index(drop=True)
        
        self.preprocessed_checklist = self.raw_checklist.iloc[:, :3]
        
        if not self.overview_df.empty:
            self.preprocessed_checklist = super()._merge_dataframes(
                self.preprocessed_checklist,
                self.overview_df,
                columns_to_keep=[0, 1, 2]
            )

    def format_checklist(self) -> pd.DataFrame:
        """ Format the raw inspection checklist data. """
        self.process_report_overview()
        
        formatting_pipeline = [
            self._filter_inspection_rows,
            self.standardize_columns,
            lambda x: self.merge_rows_by_capitalization(x, new_line=True)
        ]
        
        formatted_checklist = self._apply_formatting_pipeline(
            self.preprocessed_checklist, 
            formatting_pipeline
        )
        
        self.inspection_checklist = formatted_checklist
    
    def get_metadata(self) -> pd.DataFrame:
        """ Get formatted metadata combining all header sections.
        Returns:
            metadata(pd.DataFrame): Formatted metadata
        """
        self._set_metadata_df()
        return self.metadata

    def get_inspection_checklist(self) -> pd.DataFrame:
        """ Get formatted inspection checklist.
        Returns:
            inspection_checklist(pd.DataFrame): Formatted inspection checklist
        """
        self._set_inspection_checklist()
        return self.inspection_checklist
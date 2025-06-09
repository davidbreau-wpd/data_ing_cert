import fitz
import camelot
import pandas as pd

from utils.formatters import CSVFormatter

from loguru import logger
from pathlib import Path

from icecream import ic

class EnerconParser:
    def __init__(self, pdf_path: Path):
        """ Parser instance params 
        args:
            pdf_path (Path): Path to the pdf document.
        """
        self.pdf_path = pdf_path

        
    def _check_if_master(self):
        """ Determines if report is Master or 4-yearly according to title 
            (Note : This helps to determine how many rows "Details on order" metadata will have)
        Returns:
            bool: True if report is Master, False otherwise. """
        try:
            with fitz.open(self.pdf_path) as pdf:
                order_type = pdf[0].get_text().split('\n')[0].strip()
                is_master =  bool("MASTER" in order_type or "YEARLY" in order_type)
                return is_master
        except Exception as e:
            logger.error(f"Error while reading order type : {e}")

    def _get_converter_master_data(self) -> pd.DataFrame:
        """ Extracts master data table from page 2 
        returns:
            pd.DataFrame: "Converter Master Data" table """
            
        master_data_params = {
            'flavor': 'stream',
            'columns': ['125, 290, 390'],
            'table_areas': ['20,700,600,620'],
            'row_tol': 13,
            'split_text': True
        }
        raw_converter_data = camelot.read_pdf(
            filepath=str(self.pdf_path),
            pages='2',
            **master_data_params)
        raw_converter_df = raw_converter_data[0].df
                # extracts raw master data from pdf 
            
        formatted_converter_df = CSVFormatter.stack_column_in_pairs(raw_converter_df)
                # format data
        
        return formatted_converter_df
        
    def _get_details_on_order(self) -> pd.DataFrame:
        ''' Extracts order table from page 2
        returns:
            pd.DataFrame: "Details on order" table  '''

        is_master = self._check_if_master()
        details_on_order_params = {
            'flavor':'stream',
            'columns': ['198'],
            'table_areas': [f'20,585,600,{380 if is_master else 430}'],
            'row_tol': 10,
            'split_text': True
        }

        raw_details_on_order_data = camelot.read_pdf(
            filepath=str(self.pdf_path),
            pages='2',
            **details_on_order_params
        )
        details_on_order_df = raw_details_on_order_data[0].df
                # extracts raw details from pdf 

        formatted_details_on_order_df = CSVFormatter.merge_continuation_rows(details_on_order_df)
                # fusing cells when lines are continuing on a new row

        return formatted_details_on_order_df
    
    def _get_defects_summary(self) -> pd.DataFrame:
        ''' extracts summary table from page 2
        returns:
            pd.DataFrame: "Defects summary" table  '''
            
        is_master = self._check_if_master()
        defects_summary_params = {
            'flavor':'stream',
            'columns': ['115, 155, 235, 280, 330'],
            'table_areas': [f'20,{305 if is_master else 370},600,{275 if is_master else 340}'],
            'split_text': True,
            'edge_tol': 500  }
        raw_defects_summary_data = camelot.read_pdf(
            filepath=str(self.pdf_path),
            pages='2',
            **defects_summary_params)
                # extracts raw table 

        defects_summary_df = raw_defects_summary_data[0].df        
        stacked_summary_df = CSVFormatter.stack_column_in_pairs(defects_summary_df)
                # convert it in pandas / stack columns 

        return stacked_summary_df
    
    def get_metadata(self) -> pd.DataFrame:
        ''' Processing and merging metadata tables
        returns:
            pd.DataFrame: formatted metadata combining all header sections
        '''
        converter_master_data = self._get_converter_master_data()
        details_on_order = self._get_details_on_order()
        defects_summary = self._get_defects_summary()
                # gets three different parts of enercon report metadata
            
        metadata = pd.concat([converter_master_data, details_on_order, defects_summary], ignore_index=True)
        metadata = metadata[metadata[0].str.strip() != '']
                # fuse them 
            
        metadata.rename(columns={1: 'Metadata'}, inplace=True)
        metadata = metadata.set_index(0)
        metadata.index.name = None
                # edit final df
            
        return metadata
    
    def _get_raw_inspection_checklist_data(self) -> camelot.core.TableList:
        with fitz.open(self.pdf_path) as pdf:
            total_pages = pdf.page_count

        camelot_params = {
            'flavor': 'stream',
            'columns': ['65,450'],
            'table_areas': ['20,730,600,40'],
            'edge_tol': 700,
            'row_tol': 13,
            'split_text': False,   
            'strip_text': '\n',   
        }
        tables = camelot.read_pdf(
            filepath=str(self.pdf_path),
            pages=f"2-{total_pages}",
            **camelot_params
        )
        ic(tables)
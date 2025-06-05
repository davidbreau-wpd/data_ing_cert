import fitz
import camelot
import polars as pl 

from loguru import logger
from pathlib import Path

from icecream import ic

class Enercon_Parser:
    def __init__(self, pdf_path: Path):
        """ Parser instance params 
        Args:
            pdf_path (Path): Path to the pdf document.
        """
        self.pdf_path = pdf_path

        
    def _check_is_master(self):
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
                          
    def _get_converter_master_data(self) -> pl.DataFrame:
        master_data_params = {
            'flavor': 'stream',
            'columns': ['125, 290, 390'],
            'table_areas': ['20,700,600,620'],
            'row_tol': 13,
            'split_text': True
        }
        raw_converter_master_data = camelot.read_pdf(
            filepath=str(self.pdf_path),
            pages='2',
            **master_data_params)[0]
            # extracts raw master data from pdf 
            
        raw_cvd_pandas = raw_converter_master_data.df
        raw_cvd_polars = pl.from_pandas(raw_cvd_pandas)
        
        # ic(raw_converter_polars)
        
        
        # master_data_table = self._extract_single_page_table(2, **master_data_params)
        # master_data_df = self._convert_to_dataframe(master_data_table)
        # merged_master_data_df = self._stack_columns_in_pairs(master_data_df)
        # merged_master_data_df = merged_master_data_df.replace('', pd.NA).dropna(how='all')
        # return merged_master_data_df
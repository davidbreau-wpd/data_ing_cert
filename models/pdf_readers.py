import fitz
import camelot 
import polars as pl
import matplotlib.pyplot as plt

from loguru import logger
from pathlib import Path

class PdfReader:
    """ Class to read a pdf document using fitz """
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        
    def __enter__(self):
        """ Opens the PDF document using fitz and returns the document object. """
        try: 
            self._doc = fitz.open(self.pdf_path)
            logger.info(f"Opened document: {self.pdf_path}")
            return self
        except Exception as e:
            logger.error(f"Error opening document {self.pdf_path}: {e}")
            raise
        
    def _get_page(self, page_number: int) -> str:
        """ Retrieves the text content of specific page from the doc
        Args:
            page_number (int): The page number to retrieve
        Returns:
            str: The text content of the page
        """
        try:
            page = self._doc[page_number]
            return page.get_text()
        except Exception as e:
            logger.error(f"Error retrieving page {page_number} from document {self.pdf_path}: {e}")
            raise
    
    def __len__(self) -> int :
        """ Returns the total number of pages in the document. """
        if self._doc is None:
            # Raise an error if the document is not open when len() is called
            raise RuntimeError("Document is not opened. Use 'with Fitz_reader(pdf_path) as reader:'")
        return self._doc.page_count
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Closes the PDF document. """
        if self._doc:
            self._doc.close()
            logger.info(f"Closed document: {self.pdf_path}")
            
            
            
class TableReader:
    """ Class for extracting tables from a PDF document using Camelot. """
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
    
    
    def _get_tables(self, **kwargs) -> list[camelot.core.Table]:
        """ Extract tables from pdf document according to passed arguments
        Args:
            **kwargs: Additional keyword arguments to pass to Camelot's read_pdf function.
        Returns:
            list[camelot.core.Table]: List of extracted tables.
        Raises:
            ValueError: If no table is found.
        """
        tables = camelot.read_pdf(
            filepath=str(self.pdf_path), 
            **kwargs)
        
        if len(tables) > 0:
            return tables
        else:
            raise ValueError("No table found.")
        
    
           
    # def _get_single_table(self, page_number:int, **kwargs) -> camelot.core.Table:
    #     """ Extract table from a specific page of the pdf doc using camelot.
    #     Args:
    #         page_number (int): The page number to extract the table from.
    #         **kwargs: Additional keyword arguments to pass to Camelot's read_pdf function.
    #     Returns:
    #         camelot.core.Table: The extracted table object.
    #     Raises:
    #         ValueError: If no table is found on the specified page.
    #     """
    #     tables = camelot.read_pdf(
    #         filepath=str(self.filepath), 
    #         pages=str(page_number), 
    #         **kwargs)
        
    #     if len(tables) > 0:
    #         return tables[0]
    #     else:
    #         raise ValueError(f"No table found in page n°{page_number}")
        
        
    # def _get_multiple_pages_table(self, starting_page_number: int, ending_page_number: int, **kwargs):
    #     """ Extracts tables from a range of pages in the PDF document and combines them into a single DataFrame.
    #     Args:
    #         starting_page_number (int): The first page number to start extracting tables from.
    #         ending_page_number (int): The last page number to extract tables from.
    #         **kwargs: Additional keyword arguments to pass to Camelot's read_pdf function.
    #     Returns:
    #         pd.DataFrame: A combined DataFrame containing all extracted tables from the specified page range.
    #     Raises:
    #         ValueError: If no tables are found in the specified page range.
    #     """
    #     tables = []
        
    #     for page_number in range(starting_page_number, ending_page_number + 1):
    #         try:
    #             object_table = self._extract_single_page_table(page_number, **kwargs)
    #             table = self._convert_to_dataframe(object_table)
    #             tables.append(table)
    #         except ValueError:
    #             continue
            
    #     if not tables:
    #         raise ValueError("No table found in document") 
        
    #     final_table = pl.concat(tables, ignore_index=True)
    #     return final_table


    def visualize_camelot_parameters(self, page_number=0, **camelot_params):
        """
        Description:
            Visualizes the table extraction parameters on a specific PDF page using Camelot.
            This method helps debug and verify the accuracy of table extraction by displaying:
            - Column positions
            - Table areas
            - The extracted table structure

        Args:
            page_number (int): The page number to visualize (0-based index).
            **camelot_params: Camelot extraction parameters including:
                - columns: List of column positions as comma-separated string
                - table_areas: List of table area coordinates as comma-separated strings

        Returns:
            tuple: A tuple containing the matplotlib Figure and Axes objects for further customization.
        """

        table = self._extract_single_page_table(page_number, **camelot_params)
        
        plt.figure(figsize=(12, 16))
        camelot.plot(table, kind='contour')
        
        if 'columns' in camelot_params:
            columns = [float(x) for x in camelot_params['columns'][0].split(',')]
            for x in columns:
                plt.axvline(x=x, color='r', linestyle='--', label=f'Column {x}')
        
        if 'table_areas' in camelot_params:
            for area in camelot_params['table_areas']:
                x1, y1, x2, y2 = map(float, area.split(','))
                rect = plt.Rectangle((x1, y1), x2-x1, y2-y1,
                                   fill=False, color='m', linestyle='-',
                                   label='Zone de table')
                plt.gca().add_patch(rect)
        
        plt.title(f'Camelot parameters - Page {page_number}')
        plt.xlabel('X-coordinate')
        plt.ylabel('Y-coordinate')
        
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        return plt.gcf(), plt.gca()
    
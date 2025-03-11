import camelot, fitz, ghostscript, matplotlib.pyplot as plt, os, pandas as pd, re

class _Service_Report:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _open(self):
        self.doc = fitz.open(self.file_path)
        
    def _close(self):
        if self.doc is not None:
            self.doc.close()
            self.doc = None

    def _get_page(self, page_number: int):
        self._open()
        return self.doc[page_number].get_text()

    def _extract_single_page_table(self, page_number: int, **kwargs) -> camelot.core.Table:
        tables = camelot.read_pdf(
            self.file_path,
            pages=str(page_number),
            flavor=flavor,
            edge_tol=edge_tol,
            row_tol=row_tol,
            columns=columns)

        if len(tables) > 0:
            return tables[0]
        else:
            raise ValueError(f"No table found in page n°{page_number}")
        
    def _convert_to_dataframe(self, table) -> pd.DataFrame:
        return table.df


    def plot_column_lines(self, table, columns: list, title:str=None):
        plt.figure()
        camelot.plot(table, kind='contour')
        for col in columns:
            plt.axvline(x=col, color='r', linestyle='--', label=f'Column {col}')
        plt.title(title)
        plt.xlabel('X-coordinate')
        plt.ylabel('Y-coordinate')
        plt.legend()
        plt.show()
    


    def _extract_multiple_pages_table(self, starting_page_number: int, ending_page_number: int, flavor: str, edge_tol: int, row_tol: int, columns: list):
        tables = []
        
        for page_number in range(starting_page_number, ending_page_number + 1):
            try:
                object_table = self._extract_single_page_table(page_number, flavor, edge_tol, row_tol, columns)
                table = self._convert_to_dataframe(object_table)
                tables.append(table)
            except ValueError:
                continue
            
        if not tables:
            raise ValueError("No table found in document") 
        
        final_table = pd.concat(tables, ignore_index=True)
        return final_table
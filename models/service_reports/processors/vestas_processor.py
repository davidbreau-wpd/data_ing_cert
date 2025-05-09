import os
from pathlib import Path
from ..parsers.vestas_parser import Vestas_PDF_Parser

class Vestas_Processor:
    """
    Processor for Vestas service reports.
    Handles batch processing of PDF reports and saves extracted data to specified locations.
    """
    def __init__(self, input_folder: Path):
        self.input_folder = input_folder

    def _generate_filename(self, parser: Vestas_PDF_Parser) -> str:
        """
        Generate standardized filename based on report metadata.
        """
        metadata = parser.get_metadata()
        reason_for_call_out = str(metadata['reason_for_call_out']).replace(' ', '_').replace('/', '_')
        return f"{metadata['turbine_number']}_vestas_{metadata['service_order']}_{reason_for_call_out}"

    def process_single_report(self, file_path: Path, metadata_output_folder: Path, inspection_output_folder: Path) -> None:
        """
        Process a single Vestas PDF report and save its data.

        Args:
            file_path: Path to the PDF file
            metadata_output_folder: Where to save metadata CSV
            inspection_output_folder: Where to save inspection checklist CSV
        """
        # Initialize parser and extract data
        parser = Vestas_PDF_Parser(file_path)
        
        # Get formatted data
        metadata_df = parser.get_metadata_df()
        inspection_df = parser.get_inspection_checklist_df()
        
        # Generate filename
        filename = self._generate_filename(parser)
        
        # Save to CSV files
        metadata_df.to_csv(metadata_output_folder / f"metadata_{filename}.csv")
        inspection_df.to_csv(inspection_output_folder / f"inspection_{filename}.csv")

    def __call__(self, metadata_output_folder: Path, inspection_output_folder: Path) -> None:
        """
        Process all PDF files in the input folder.

        Args:
            metadata_output_folder: Directory for metadata CSV files
            inspection_output_folder: Directory for inspection checklist CSV files
        """
        for pdf_file in os.listdir(self.input_folder):
            if pdf_file.lower().endswith('.pdf'):
                file_path = self.input_folder / pdf_file
                try:
                    self.process_single_report(file_path, metadata_output_folder, inspection_output_folder)
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}")
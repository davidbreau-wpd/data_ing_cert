import os
from pathlib import Path
from ..parsers.enercon_parser import Enercon_PDF_Parser

class Enercon_Processor:
    """
    Processor for Enercon service reports.
    Handles batch processing of PDF reports and saves extracted data to specified locations.
    """
    def __init__(self, input_folder: Path):
        self.input_folder = input_folder

    def _generate_filename(self, parser: Enercon_PDF_Parser) -> str:
        """
        Generate standardized filename based on report metadata.
        """
        metadata_df = parser.get_metadata_df()
        order_type = parser.order_type if hasattr(parser, 'order_type') else "unknown"
        order_number = metadata_df.loc["Order number", "Metadata"] if "Order number" in metadata_df.index else "unknown"
        serial_number = metadata_df.loc["Serial number", "Metadata"] if "Serial number" in metadata_df.index else "unknown"
        
        return f"{serial_number}_enercon_{order_type.replace(' ', '_').lower()}_{order_number}"

    def process_single_report(self, file_path: Path, metadata_output_folder: Path, inspection_checklist_output_folder: Path) -> None:
        """
        Process a single Enercon PDF report and save its data.

        Args:
            file_path: Path to the PDF file
            metadata_output_folder: Where to save metadata CSV
            inspection_checklist_output_folder: Where to save inspection checklist CSV
        """
        # Initialize parser and extract data
        parser = Enercon_PDF_Parser(file_path)
        
        # Get formatted data
        metadata_df = parser.get_metadata_df()
        inspection_df = parser.get_inspection_checklist_df()
        
        # Generate filename
        filename = self._generate_filename(parser)
        
        # Save to CSV files
        metadata_df.to_csv(metadata_output_folder / f"metadata_{filename}.csv")
        inspection_df.to_csv(inspection_checklist_output_folder / f"inspection_{filename}.csv")

    def __call__(self, metadata_output_folder: Path, inspection_checklist_output_folder: Path) -> None:
        """
        Process all PDF files in the input folder.

        Args:
            metadata_output_folder: Directory for metadata CSV files
            inspection_checklist_output_folder: Directory for inspection checklist CSV files
        """
        metadata_output_folder.mkdir(parents=True, exist_ok=True)
        inspection_checklist_output_folder.mkdir(parents=True, exist_ok=True)

        for pdf_file in os.listdir(self.input_folder):
            if str(pdf_file).lower().endswith('.pdf'):  # Convert to str before calling lower()
                file_path = self.input_folder / pdf_file
                try:
                    self.process_single_report(file_path, metadata_output_folder, inspection_checklist_output_folder)
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}")
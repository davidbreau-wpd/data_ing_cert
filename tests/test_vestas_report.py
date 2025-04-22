import pytest
import pandas as pd
from models.vestas_report import Vestas_Report

class TestVestasReport:
    def test_set_order_type(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "Service Report\nOther content"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Vestas_Report("test.pdf")
        
        assert report.order_type == "Service Report"

    def test_set_order_type_error(self, mocker):
        mocker.patch('fitz.open', side_effect=Exception("Test error"))
        
        report = Vestas_Report("test.pdf")
        
        assert report.order_type is None

    def test_extract_inspection_checklist(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_doc.__len__.return_value = 5
        mock_doc.__enter__.return_value = mock_doc
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Vestas_Report("test.pdf")
        mock_df = pd.DataFrame()
        mocker.patch.object(report, '_get_multiple_pages_table', return_value=mock_df)
        
        result = report.extract_inspection_checklist()
        
        assert isinstance(result, pd.DataFrame)

    def test_filter_inspection_rows(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "Service Report"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Vestas_Report("test.pdf")
        df = pd.DataFrame({
            0: ['Header', 'Inspection', 'Test1', 'Test2', 'Signature', 'Footer'],
            1: ['A', 'B', 'C', 'D', 'E', 'F']
        })
        
        result = report._filter_inspection_rows(df)
        
        assert len(result) == 2
        assert result.iloc[0][0] == 'Test1'
        assert result.iloc[1][0] == 'Test2'

    def test_process_report(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "Service Report"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Vestas_Report("test.pdf")
        mock_inspection = pd.DataFrame()
        mocker.patch.object(report, 'extract_inspection_checklist', return_value=mock_inspection)
        mocker.patch.object(report, '_filter_inspection_rows', return_value=mock_inspection)
        mock_save = mocker.patch.object(report, 'save_table_to_csv')
        
        report._process_report(None, "inspection_folder")
        
        mock_save.assert_called_once_with(
            table=mock_inspection,
            name="inspection_service_report",
            folder_path="inspection_folder"
        )
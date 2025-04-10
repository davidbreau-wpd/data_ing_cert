import pytest
import pandas as pd
from models.enercon_report import Enercon_Report

class TestEnerconReport:
    def test_set_order_type(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER\nOther content"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        
        assert report.order_type == "MASTER SERVICE ORDER"
        
    def test_set_order_type_error(self, mocker):
        mocker.patch('fitz.open', side_effect=Exception("Test error"))
        
        report = Enercon_Report("test.pdf")
        
        assert report.order_type is None

    def test_check_is_master_with_master_order(self):
        report = Enercon_Report("test.pdf")
        report.order_type = "MASTER SERVICE ORDER"
        
        report._check_is_master()
        
        assert report.is_master is True

    def test_check_is_master_with_yearly_order(self):
        report = Enercon_Report("test.pdf")
        report.order_type = "4-YEARLY SERVICE ORDER"
        
        report._check_is_master()
        
        assert report.is_master is True

    def test_check_is_master_with_regular_order(self):
        report = Enercon_Report("test.pdf")
        report.order_type = "REGULAR SERVICE ORDER"
        
        report._check_is_master()
        
        assert report.is_master is False

    def test_get_converter_master_data(self, mocker, mock_camelot_table):
        report = Enercon_Report("test.pdf")
        mock_extract = mocker.patch.object(report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        mock_df = pd.DataFrame({
            0: ['Parameter', 'Value'],
            1: ['Setting', 'Data'],
            2: ['Config', 'Info']
        })
        mocker.patch.object(report, '_convert_to_dataframe', return_value=mock_df)
        
        result = report._get_converter_master_data()
        
        assert isinstance(result, pd.DataFrame)
        mock_extract.assert_called_once()

    def test_get_converter_master_data_no_table(self, mocker, test_pdf_path):
        report = Enercon_Report(test_pdf_path)
        mocker.patch.object(report, '_extract_single_page_table', side_effect=ValueError("No table found"))
        
        with pytest.raises(ValueError, match="No table found"):
            report._get_converter_master_data()

    def test_get_details_on_order_not_master(self, mocker, mock_camelot_table):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "REGULAR SERVICE ORDER"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mock_extract = mocker.patch.object(report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        result = report._get_details_on_order()
        
        mock_extract.assert_called_once_with(2, **{
            'flavor': 'stream',
            'columns': ['195'],
            'table_areas': ['20,590,600,420'],
            'edge_tol': 700,
            'row_tol': 10,
            'split_text': True,
            'strip_text': '\n'
        })

    def test_get_details_on_order_with_master(self, mocker, mock_camelot_table):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mock_extract = mocker.patch.object(report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        report._get_details_on_order()
        
        mock_extract.assert_called_once_with(2, **{
            'flavor': 'stream',
            'columns': ['195'],
            'table_areas': ['20,590,600,380'],
            'edge_tol': 700,
            'row_tol': 10,
            'split_text': True,
            'strip_text': '\n'
        })

    def test_get_defects_summary_master(self, mocker, mock_camelot_table):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mock_extract = mocker.patch.object(report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        report._get_defects_summary()
        
        mock_extract.assert_called_once_with(2, **{
            'flavor': 'stream',
            'columns': ['115, 155, 235, 280, 330'],
            'table_areas': ['20,265,600,305'],
            'edge_tol': 700,
            'row_tol': 13,
            'split_text': True,
            'strip_text': '\n'
        })

    def test_extract_inspection_checklist(self, mocker, mock_camelot_table):
        mock_doc = mocker.MagicMock()
        mock_doc.__len__.return_value = 5
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mocker.patch.object(report, '_get_multiple_pages_table', return_value=pd.DataFrame())
        
        result = report.extract_inspection_checklist()
        
        assert isinstance(result, pd.DataFrame)

    def test_filter_inspection_rows(self, mocker):
        report = Enercon_Report("test.pdf")
        df = pd.DataFrame({
            0: ['Header', 'Details', 'Test1', 'Test2', 'Signature', 'Footer'],
            1: ['A', 'B', 'C', 'D', 'E', 'F']
        })
        
        result = report._filter_inspection_rows(df)
        
        assert len(result) == 2
        assert result.iloc[0][0] == 'Test1'
        assert result.iloc[1][0] == 'Test2'

    def test_set_filename(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mock_metadata = pd.DataFrame({
            'Metadata': ['123', '456']
        }, index=['Order number', 'Serial number'])
        report.metadata_df = mock_metadata
        report.order_type = "MASTER SERVICE ORDER"
        
        result = report._set_filename()
        
        assert result == "456_enercon_master_service_order_123"

    def test_process_report(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        mock_metadata = pd.DataFrame({
            'Metadata': ['123', '456']
        }, index=['Order number', 'Serial number'])
        report.metadata_df = mock_metadata
        mock_inspection = pd.DataFrame()
        
        mocker.patch.object(report, 'get_metadata', return_value=mock_metadata)
        mocker.patch.object(report, 'extract_inspection_checklist', return_value=mock_inspection)
        mocker.patch.object(report, 'format_table', return_value=mock_inspection)
        mock_save = mocker.patch.object(report, 'save_table_to_csv')
        
        report._process_report("metadata_folder", "inspection_folder")
        
        assert mock_save.call_count == 2
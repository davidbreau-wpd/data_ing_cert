import pytest
import pandas as pd
from models.enercon_report import Enercon_Report

class TestEnerconReport:
    def test_set_order_type(self, mocker):
        # Arrange
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "MASTER SERVICE ORDER\nOther content"
        mock_doc.__enter__.return_value = [mock_page]
        mocker.patch('fitz.open', return_value=mock_doc)
        
        report = Enercon_Report("test.pdf")
        
        # Assert
        assert report.order_type == "MASTER SERVICE ORDER"
        
    def test_set_order_type_error(self, mocker):
        # Arrange
        mocker.patch('fitz.open', side_effect=Exception("Test error"))
        
        # Act
        report = Enercon_Report("test.pdf")
        
        # Assert
        assert report.order_type is None

    def test_check_is_master_with_master_order(self):
        # Arrange
        report = Enercon_Report("test.pdf")
        report.order_type = "MASTER SERVICE ORDER"
        
        # Act
        report._check_is_master()
        
        # Assert
        assert report.is_master is True

    def test_check_is_master_with_yearly_order(self):
        # Arrange
        report = Enercon_Report("test.pdf")
        report.order_type = "4-YEARLY SERVICE ORDER"
        
        # Act
        report._check_is_master()
        
        # Assert
        assert report.is_master is True

    def test_check_is_master_with_regular_order(self):
        # Arrange
        report = Enercon_Report("test.pdf")
        report.order_type = "REGULAR SERVICE ORDER"
        
        # Act
        report._check_is_master()
        
        # Assert
        assert report.is_master is False

    def test_get_converter_master_data(self, mocker, mock_camelot_table):
        # Arrange
        report = Enercon_Report("test.pdf")
        mock_extract = mocker.patch.object(report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        # Prepare mock data
        mock_df = pd.DataFrame({
            0: ['Parameter', 'Value'],
            1: ['Setting', 'Data'],
            2: ['Config', 'Info']
        })
        mocker.patch.object(report, '_convert_to_dataframe', return_value=mock_df)
        
        # Act
        result = report._get_converter_master_data()
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        mock_extract.assert_called_once()

    def test_get_converter_master_data_no_table(self, mocker):
        # Arrange
        report = Enercon_Report("test.pdf")
        mocker.patch.object(report, '_extract_single_page_table', side_effect=ValueError("No table found"))
        
        # Act & Assert
        with pytest.raises(ValueError, match="No table found"):
            report._get_converter_master_data()
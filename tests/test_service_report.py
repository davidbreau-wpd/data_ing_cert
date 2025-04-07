import pytest
import pandas as pd
from models.service_report import _Service_Report

class TestServiceReport:
    def test_get_page(self, mocker):
        # Arrange
        mock_doc = mocker.MagicMock()
        mock_doc.__getitem__().get_text.return_value = "Test page content"
        mock_fitz_open = mocker.patch('fitz.open', return_value=mock_doc)
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report._get_page(0)
        
        # Assert
        assert result == "Test page content"
        mock_fitz_open.assert_called_once_with("test.pdf")

    def test_extract_single_page_table(self, mocker):
        # Arrange
        mock_table = mocker.MagicMock()
        mock_camelot = mocker.patch('camelot.read_pdf', return_value=[mock_table])
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report._extract_single_page_table(1)
        
        # Assert
        assert result == mock_table
        mock_camelot.assert_called_once_with("test.pdf", pages="1")

    def test_merge_continuation_lines(self):
        # Arrange
        input_df = pd.DataFrame({
            0: ['1', '', '2'],
            1: ['Main item', 'continuation', 'Another item'],
            2: ['OK', 'NOK', 'OK']
        })
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report.merge_continuation_lines(input_df)
        
        # Assert
        assert len(result) == 2  # Should have merged rows
        assert result.iloc[0, 1] == "Main item continuation"  # Should merge text

    def test_standardize_columns(self):
        # Arrange
        input_df = pd.DataFrame({
            0: ['1'],
            1: ['Item'],
            2: ['OK']
        })
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report.standardize_columns(input_df)
        
        # Assert
        assert list(result.columns) == ['no', 'check_item', 'result']

    def test_get_multiple_pages_table(self, mocker, mock_camelot_table, sample_dataframe):
        # Arrange
        service_report = _Service_Report("test.pdf")
        
        # Mock _extract_single_page_table to return mock table for page 1 and raise ValueError for page 2
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table')
        mock_extract.side_effect = [
            mock_camelot_table,  # Page 1 succeeds
            ValueError(),        # Page 2 fails
            mock_camelot_table   # Page 3 succeeds
        ]
        
        # Mock _convert_to_dataframe to return sample_dataframe
        mock_convert = mocker.patch.object(service_report, '_convert_to_dataframe')
        mock_convert.return_value = sample_dataframe
        
        # Act
        result = service_report._get_multiple_pages_table(1, 3)
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_dataframe) * 2  # Should have 2 successful pages
        mock_extract.assert_has_calls([
            mocker.call(1),
            mocker.call(2),
            mocker.call(3)
        ])
        assert mock_convert.call_count == 2
    
    def test_get_multiple_pages_table_no_tables(self, mocker):
        # Arrange
        service_report = _Service_Report("test.pdf")
        
        # Mock _extract_single_page_table to always raise ValueError
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table')
        mock_extract.side_effect = ValueError()
        
        # Act & Assert
        with pytest.raises(ValueError, match="No table found in document"):
            service_report._get_multiple_pages_table(1, 2)

    def test_convert_to_dataframe(self, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        result = service_report._convert_to_dataframe(mock_camelot_table)
        assert isinstance(result, pd.DataFrame)
    
    def test_plot_column_lines(self, mocker, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        mock_plt = mocker.patch('matplotlib.pyplot')
        
        service_report.plot_column_lines(mock_camelot_table, columns=[65, 330])
        
        mock_plt.figure.assert_called_once()
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65, color='r', linestyle='--', label='Column 65'),
            mocker.call(x=330, color='r', linestyle='--', label='Column 330')
        ])

    def test_apply_formatting_pipeline(self):
        service_report = _Service_Report("test.pdf")
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        
        def mock_func1(df): return df * 2
        def mock_func2(df): return df + 1
        
        result = service_report._apply_formatting_pipeline(df, [mock_func1, mock_func2])
        
        expected = pd.DataFrame({'A': [3, 5], 'B': [7, 9]})
        pd.testing.assert_frame_equal(result, expected)

    def test_save_table_to_csv(self, mocker, tmp_path):
        service_report = _Service_Report("test.pdf")
        df = pd.DataFrame({'test': [1, 2, 3]})
        
        mock_makedirs = mocker.patch('os.makedirs')
        mock_to_csv = mocker.patch.object(df, 'to_csv')
        
        service_report.save_table_to_csv(df, "test_output", str(tmp_path))
        
        mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)
        mock_to_csv.assert_called_once()

    def test_visualize_camelot_parameters(self, mocker, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        mock_plt = mocker.patch('matplotlib.pyplot')
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        service_report.visualize_camelot_parameters(0, columns=['65,330'])
        
        mock_plt.figure.assert_called_once()
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65.0, color='r', linestyle='--', label='Colonne 65.0'),
            mocker.call(x=330.0, color='r', linestyle='--', label='Colonne 330.0')
        ])
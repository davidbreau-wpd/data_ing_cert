import pytest
import pandas as pd
import logging
from models.service_report import _Service_Report

class TestServiceReport:
    def test_get_page(self, mocker):
        # Arrange
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "Test page content"
        mock_doc.__enter__().__getitem__.return_value = mock_page
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
        
        # Mock matplotlib.pyplot
        mock_plt = mocker.patch('models.service_report.plt')
        
        # Mocker camelot.plot
        mock_camelot_plot = mocker.patch('camelot.plot')
        
        # Appeler la méthode à tester
        service_report.plot_column_lines(mock_camelot_table, columns=[65, 330])
        
        # Vérifier les appels
        mock_plt.figure.assert_called_once()
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65, color='r', linestyle='--', label='Column 65'),
            mocker.call(x=330, color='r', linestyle='--', label='Column 330')
        ])
        mock_plt.show.assert_called_once()

    def test_visualize_camelot_parameters(self, mocker, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        
        # Mock matplotlib.pyplot
        mock_plt = mocker.patch('models.service_report.plt')
        mock_gca = mocker.MagicMock()
        mock_plt.gca.return_value = mock_gca
        mock_gca.get_legend_handles_labels.return_value = ([], [])  # Mock empty handles and labels
        
        # Mocker camelot.plot
        mock_camelot_plot = mocker.patch('camelot.plot')
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        service_report.visualize_camelot_parameters(0, columns=['65,330'])
        
        # Vérifier les appels
        mock_plt.figure.assert_called_once_with(figsize=(12, 16))
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65.0, color='r', linestyle='--', label='Colonne 65.0'),
            mocker.call(x=330.0, color='r', linestyle='--', label='Colonne 330.0')
        ])

    def test_apply_formatting_pipeline(self):
        # Arrange
        input_df = pd.DataFrame({
            0: ['1', '', '2'],
            1: ['Main item', 'continuation', 'Another item'],
            2: ['OK', 'NOK', 'OK']
        })
        
        def mock_clean1(df):
            return df.fillna('')
            
        def mock_clean2(df):
            return df[df[0] != '']
            
        service_report = _Service_Report("test.pdf")
        cleaning_pipeline = [mock_clean1, mock_clean2]
        
        # Act
        result = service_report._apply_formatting_pipeline(input_df, cleaning_pipeline)
        
        # Assert
        assert len(result) == 2
        assert result.iloc[0, 0] == '1'
        assert result.iloc[1, 0] == '2'

    def test_save_table_to_csv(self, tmp_path, mocker):
        # Arrange
        mock_logging = mocker.patch('models.service_report.logging')
        input_df = pd.DataFrame({
            'no': ['1', '2'],
            'check_item': ['Item 1', 'Item 2'],
            'result': ['OK', 'NOK']
        })
        
        service_report = _Service_Report("test.pdf")
        output_folder = tmp_path / "output"
        
        # Act
        service_report.save_table_to_csv(input_df, "test_table", str(output_folder))
        
        # Assert
        assert (output_folder / "test_table.csv").exists()
        saved_df = pd.read_csv(output_folder / "test_table.csv", index_col=0)
        assert len(saved_df) == 2
        mock_logging.info.assert_called_once()

    def test_stack_columns_in_pairs(self):
        # Arrange
        input_df = pd.DataFrame({
            0: ['A', 'C'],
            1: ['B', 'D'],
            2: ['E', 'G'],
            3: ['F', 'H']
        })
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report._stack_columns_in_pairs(input_df)
        
        # Assert
        assert len(result) == 4  # Should have doubled the rows
        assert list(result.columns) == [0, 1]  # Should have only 2 columns
        assert result.iloc[0, 0] == 'A'
        assert result.iloc[0, 1] == 'B'
        assert result.iloc[2, 0] == 'E'
        assert result.iloc[2, 1] == 'F'

    def test_merge_rows_by_capitalization(self):
        # Arrange
        input_df = pd.DataFrame({
            0: ['Main Item', 'continuation text', 'Another Item', 'more details'],
            1: ['Value 1', 'Extra 1', 'Value 2', '']
        })
        
        service_report = _Service_Report("test.pdf")
        
        # Act
        result = service_report.merge_rows_by_capitalization(input_df)
        
        # Assert
        assert len(result) == 2  # Should have merged into 2 rows
        assert result.iloc[0, 0] == 'Main Item continuation text'
        assert result.iloc[1, 0] == 'Another Item more details'
        assert result.iloc[0, 1] == 'Value 1'
        assert result.iloc[1, 1] == 'Value 2'
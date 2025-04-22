import pytest
import pandas as pd
import logging
from models.service_report import _Service_Report

class TestServiceReport:
    def test_get_page(self, mocker):
        mock_doc = mocker.MagicMock()
        mock_page = mocker.MagicMock()
        mock_page.get_text.return_value = "Test page content"
        mock_doc.__enter__().__getitem__.return_value = mock_page
        mock_fitz_open = mocker.patch('fitz.open', return_value=mock_doc)
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report._get_page(0)
        
        assert result == "Test page content"
        mock_fitz_open.assert_called_once_with("test.pdf")

    def test_extract_single_page_table(self, mocker):
        mock_table = mocker.MagicMock()
        mock_camelot = mocker.patch('camelot.read_pdf', return_value=[mock_table])
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report._extract_single_page_table(1)
        
        assert result == mock_table
        mock_camelot.assert_called_once_with("test.pdf", pages="1")

    def test_merge_continuation_lines(self):
        input_df = pd.DataFrame({
            0: ['1', '', '2'],
            1: ['Main item', 'continuation', 'Another item'],
            2: ['OK', 'NOK', 'OK']
        })
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report.merge_continuation_lines(input_df)
        
        assert len(result) == 2
        assert result.iloc[0, 1] == "Main item continuation"

    def test_standardize_columns(self):
        input_df = pd.DataFrame({
            0: ['1'],
            1: ['Item'],
            2: ['OK']
        })
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report.standardize_columns(input_df)
        
        assert list(result.columns) == ['no', 'check_item', 'result']

    def test_get_multiple_pages_table(self, mocker, mock_camelot_table, sample_dataframe):
        service_report = _Service_Report("test.pdf")
        
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table')
        mock_extract.side_effect = [
            mock_camelot_table,
            ValueError(),
            mock_camelot_table
        ]
        
        mock_convert = mocker.patch.object(service_report, '_convert_to_dataframe')
        mock_convert.return_value = sample_dataframe
        
        result = service_report._get_multiple_pages_table(1, 3)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_dataframe) * 2
        mock_extract.assert_has_calls([
            mocker.call(1),
            mocker.call(2),
            mocker.call(3)
        ])
        assert mock_convert.call_count == 2
    
    def test_get_multiple_pages_table_no_tables(self, mocker):
        service_report = _Service_Report("test.pdf")
        
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table')
        mock_extract.side_effect = ValueError()
        
        with pytest.raises(ValueError, match="No table found in document"):
            service_report._get_multiple_pages_table(1, 2)

    def test_convert_to_dataframe(self, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        result = service_report._convert_to_dataframe(mock_camelot_table)
        assert isinstance(result, pd.DataFrame)
    
    def test_plot_column_lines(self, mocker, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        
        mock_plt = mocker.patch('models.service_report.plt')
        
        mock_camelot_plot = mocker.patch('camelot.plot')
        
        service_report.plot_column_lines(mock_camelot_table, columns=[65, 330])
        
        mock_plt.figure.assert_called_once()
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65, color='r', linestyle='--', label='Column 65'),
            mocker.call(x=330, color='r', linestyle='--', label='Column 330')
        ])
        mock_plt.show.assert_called_once()

    def test_visualize_camelot_parameters(self, mocker, mock_camelot_table):
        service_report = _Service_Report("test.pdf")
        
        mock_plt = mocker.patch('models.service_report.plt')
        mock_gca = mocker.MagicMock()
        mock_plt.gca.return_value = mock_gca
        mock_gca.get_legend_handles_labels.return_value = ([], [])
        
        mock_camelot_plot = mocker.patch('camelot.plot')
        mock_extract = mocker.patch.object(service_report, '_extract_single_page_table', return_value=mock_camelot_table)
        
        service_report.visualize_camelot_parameters(0, columns=['65,330'])
        
        mock_plt.figure.assert_called_once_with(figsize=(12, 16))
        mock_plt.axvline.assert_has_calls([
            mocker.call(x=65.0, color='r', linestyle='--', label='Colonne 65.0'),
            mocker.call(x=330.0, color='r', linestyle='--', label='Colonne 330.0')
        ])

    def test_apply_formatting_pipeline(self):
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
        
        result = service_report._apply_formatting_pipeline(input_df, cleaning_pipeline)
        
        assert len(result) == 2
        assert result.iloc[0, 0] == '1'
        assert result.iloc[1, 0] == '2'

    def test_save_table_to_csv(self, tmp_path, mocker):
        mock_logging = mocker.patch('models.service_report.logging')
        input_df = pd.DataFrame({
            'no': ['1', '2'],
            'check_item': ['Item 1', 'Item 2'],
            'result': ['OK', 'NOK']
        })
        
        service_report = _Service_Report("test.pdf")
        output_folder = tmp_path / "output"
        
        service_report.save_table_to_csv(input_df, "test_table", str(output_folder))
        
        assert (output_folder / "test_table.csv").exists()
        saved_df = pd.read_csv(output_folder / "test_table.csv", index_col=0)
        assert len(saved_df) == 2
        mock_logging.info.assert_called_once()

    def test_stack_columns_in_pairs(self):
        input_df = pd.DataFrame({
            0: ['A', 'C'],
            1: ['B', 'D'],
            2: ['E', 'G'],
            3: ['F', 'H']
        })
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report._stack_columns_in_pairs(input_df)
        
        assert len(result) == 4
        assert list(result.columns) == [0, 1]
        assert result.iloc[0, 0] == 'A'
        assert result.iloc[0, 1] == 'B'
        assert result.iloc[2, 0] == 'E'
        assert result.iloc[2, 1] == 'F'

    def test_merge_rows_by_capitalization(self):
        input_df = pd.DataFrame({
            0: ['Main Item', 'continuation text', 'Another Item', 'more details'],
            1: ['Value 1', 'Extra 1', 'Value 2', '']
        })
        
        service_report = _Service_Report("test.pdf")
        
        result = service_report.merge_rows_by_capitalization(input_df)
        
        assert len(result) == 2
        assert result.iloc[0, 0] == 'Main Item continuation text'
        assert result.iloc[1, 0] == 'Another Item more details'
        assert result.iloc[0, 1] == 'Value 1'
        assert result.iloc[1, 1] == 'Value 2'
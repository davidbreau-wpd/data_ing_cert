import pytest
import pandas as pd
import camelot
from unittest.mock import MagicMock

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'test': [1, 2, 3],
        'other': ['a', 'b', 'c']
    })

@pytest.fixture
def empty_dataframe():
    return pd.DataFrame()

@pytest.fixture
def sample_inspection_df():
    return pd.DataFrame({
        0: ['1', '2', '3'],
        1: ['Check item 1', 'Check item 2', 'Check item 3'],
        2: ['OK', 'NOK', 'N/A']
    })

@pytest.fixture
def mock_camelot_table():
    mock_table = MagicMock(spec=camelot.core.Table)
    mock_table.df = pd.DataFrame({
        0: ['1', '2'],
        1: ['Item', 'Another item'],
        2: ['OK', 'NOK']
    })
    return mock_table
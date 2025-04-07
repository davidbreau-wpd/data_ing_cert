import pytest
import pandas as pd
from models.utils import log_errors, dataframe_required

def test_log_errors_decorator():
    @log_errors
    def function_that_raises():
        raise ValueError("Test error")
    
    @log_errors
    def function_that_succeeds():
        return "Success"
    
    # Test error case
    result = function_that_raises()
    assert result is None
    
    # Test success case
    result = function_that_succeeds()
    assert result == "Success"

def test_dataframe_required_decorator(sample_dataframe, empty_dataframe):
    @dataframe_required
    def process_df(df):
        return df
    
    # Test with valid DataFrame
    result = process_df(sample_dataframe)
    assert isinstance(result, pd.DataFrame)
    
    # Test with empty DataFrame
    result = process_df(empty_dataframe)
    assert isinstance(result, pd.DataFrame)
    
    # Test with None
    with pytest.raises(ValueError):
        process_df(None)
    
    # Test with non-DataFrame
    with pytest.raises(ValueError):
        process_df("not a dataframe")
import pytest
import pandas as pd
from models.utils import log_errors, dataframe_required

def test_log_errors_decorator(caplog):
    @log_errors
    def function_that_raises():
        raise ValueError("Test error")
    
    # Test error case - capture l'exception mais vérifie le log
    with pytest.raises(ValueError, match="Test error"):
        function_that_raises()
    
    assert "Error in function_that_raises" in caplog.text

def test_dataframe_required_decorator(sample_dataframe):
    @dataframe_required
    def process_df(self, df):
        return df
    
    class DummyClass:
        pass
    
    instance = DummyClass()
    
    # Test with valid DataFrame
    result = process_df(instance, sample_dataframe)
    assert isinstance(result, pd.DataFrame)
    assert result.equals(sample_dataframe)
    
    # Test with None
    with pytest.raises(TypeError, match="process_df requires pandas DataFrame"):
        process_df(instance, None)
    
    # Test with invalid type
    with pytest.raises(TypeError, match="process_df requires pandas DataFrame"):
        process_df(instance, "not a dataframe")
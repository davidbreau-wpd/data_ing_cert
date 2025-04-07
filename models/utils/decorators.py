import logging, pandas as pd

def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

def dataframe_required(func):
    """Decorator that validates the input is a non-empty pandas DataFrame"""
    def wrapper(self, df: pd.DataFrame, *args, **kwargs):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{func.__name__} requires pandas DataFrame, got {type(df)}")
        if df.empty:
            raise ValueError(f"{func.__name__} received empty DataFrame")
        return func(self, df, *args, **kwargs)
    return wrapper
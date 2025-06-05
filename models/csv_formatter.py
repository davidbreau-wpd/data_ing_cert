import polars as pl


from icecream import ic

class CSVFormatter:
    """ Class containing generic functions to edit CSV's extracted from tables in reports """
    def stack_column_in_pairs(df: pl.DataFrame) -> pl.DataFrame:
        """ """
        df.columns = [i % 2 for i in range(len(df.columns))] 
            # Rename columns to 0,1,0,1 and so on
        
        key_value_pairs = []
        for i in range(0, len(df.columns), 2):
            pair = df.iloc[:, i:i+2]
            key_value_pairs.append(pair)
                # stores fragmented dataframe in pairs of value-key columns in 

        stacked_df = pl.concat(key_value_pairs, how='vertical')
            # merge all parts in one

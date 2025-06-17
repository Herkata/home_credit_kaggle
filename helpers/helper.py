import polars as pl
import numpy as np
import pandas as pd

def optimize_memory_usage(df):
    for col in df.columns:
        dtype = df[col].dtype
        if dtype == pl.Float64:
            df = df.with_columns(pl.col(col).cast(pl.Float32))
        elif dtype == pl.Int64:
            df = df.with_columns(pl.col(col).cast(pl.Int32))
    return df

def calculate_missing_proportion(df):
    if isinstance(df, pl.DataFrame):
        missing_proportion = df.null_count() / len(df)
    elif isinstance(df, pd.DataFrame):
        missing_proportion = df.isnull().mean()
    else:
        raise TypeError("Unsupported DataFrame type. Please provide a Polars or Pandas DataFrame.")
    return missing_proportion

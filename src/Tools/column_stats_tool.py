import pandas as pd

def generate_column_stats(df: pd.DataFrame) -> dict:
    stats = {}
    for col in df.columns:
        stats[col] = {
            "nulls": df[col].isnull().sum(),
            "unique": df[col].nunique(),
            "min": df[col].min() if pd.api.types.is_numeric_dtype(df[col]) else None,
            "max": df[col].max() if pd.api.types.is_numeric_dtype(df[col]) else None,
            "std_dev": df[col].std() if pd.api.types.is_numeric_dtype(df[col]) else None,
            "distribution": df[col].value_counts().to_dict()
        }
    return stats
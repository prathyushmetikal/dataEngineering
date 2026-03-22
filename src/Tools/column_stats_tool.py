import pandas as pd

def generate_column_stats(df: pd.DataFrame) -> dict:
    stats = {}
    for col in df.columns:
        col_stats = {
            "nulls": int(df[col].isnull().sum()),
            "unique": int(df[col].nunique()),
            # ← dropna=True removes nan keys from distribution entirely
            "distribution": {
                str(k): int(v)              # ← cast keys to str, values to int
                for k, v in df[col].value_counts(dropna=True).items()
            }
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats["min"] = float(df[col].min()) if not df[col].isnull().all() else None
            col_stats["max"] = float(df[col].max()) if not df[col].isnull().all() else None
            col_stats["std_dev"] = float(df[col].std()) if not df[col].isnull().all() else None
        else:
            col_stats["min"] = None
            col_stats["max"] = None
            col_stats["std_dev"] = None

        stats[col] = col_stats

    return stats
# src/tools/data_cleaning_tool.py
import pandas as pd
import numpy as np

def clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill null values based on column type:
    - Numeric (int/float): mean
    - Categorical (object/string): mode
    - Boolean: mode (most frequent True/False)
    - Datetime: median date
    - Timedelta: median duration
    - Other types: leave as-is
    """
    cleaned_df = df.copy()

    for col in cleaned_df.columns:
        series = cleaned_df[col]

        # Numeric (int/float)
        # Guard: skip if all nulls (mean would be NaN, filling with NaN changes nothing)
        if pd.api.types.is_numeric_dtype(series):
            if series.isna().all():
                continue
            mean_val = series.mean()
            cleaned_df[col] = series.fillna(mean_val)  # ← avoid inplace + chained assignment warning

        # Datetime
        elif pd.api.types.is_datetime64_any_dtype(series):
            if series.isna().all():
                continue
            median_date = series.dropna().sort_values().iloc[len(series.dropna()) // 2]  # ← .median() unreliable on datetime in some pandas versions
            cleaned_df[col] = series.fillna(median_date)

        # Timedelta
        elif pd.api.types.is_timedelta64_dtype(series):
            if series.isna().all():
                continue
            median_delta = series.dropna().median()
            cleaned_df[col] = series.fillna(median_delta)

        # Boolean — must come BEFORE object check, bools can appear as object dtype
        elif pd.api.types.is_bool_dtype(series):
            mode_val = series.mode()[0] if not series.mode().empty else False
            cleaned_df[col] = series.fillna(mode_val)

        # Strings / categorical
        # ← is_categorical_dtype removed in pandas 2.1, use isinstance check instead
        elif pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            if series.isna().all():
                cleaned_df[col] = series.fillna("Unknown")
                continue
            mode_val = series.mode()[0] if not series.mode().empty else "Unknown"
            cleaned_df[col] = series.fillna(mode_val)

        # Fallback — leave as-is
        else:
            cleaned_df[col] = series

    return cleaned_df
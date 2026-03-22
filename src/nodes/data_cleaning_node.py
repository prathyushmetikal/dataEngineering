# src/nodes/data_cleaning_node.py
import pandas as pd
from src.tools.data_cleaning_tool import clean_nulls

def data_cleaning_node(state: dict) -> dict:
    """
    Node that reads CSV, cleans nulls, and returns updated state.
    """
    df = pd.read_csv(state["file_path"], parse_dates=True)
    cleaned_df = clean_nulls(df)

    # Save cleaned data
    cleaned_path = state.get("cleaned_path", "cleaned_data.csv")
    cleaned_df.to_csv(cleaned_path, index=False)
    iterations = state.get("cleaning_iterations", 0) + 1  # ← ADD THIS
    return {
        **state,
        "cleaning_done": True, 
        "cleaned_file": cleaned_path,
        #"file_path": cleaned_path, 
        "cleaning_iterations": iterations, 
        #"logs": ["Null values imputed with mean/mode/median depending on type."]
        "logs": state.get("logs", []) + [f"Cleaning pass {iterations} done."] 
    }
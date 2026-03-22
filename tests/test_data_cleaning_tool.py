# tests/test_data_cleaning_node.py
import os
import pandas as pd
import pytest
import json
from src.nodes.data_cleaning_node import data_cleaning_node

@pytest.fixture
def sample_csv():
    # Create a sample CSV with nulls
    data = {
        "age": [25, None, 40, 35],
        "gender": ["Male", "Female", None, "Female"],
        "is_insured": [True, None, False, True],
        "visit_date": [pd.NaT, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01"), None]
    }
    df = pd.DataFrame(data)
    file_path =  "src/testreports/sample.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

def test_data_cleaning_node(sample_csv):
    # Step 1: Run cleaning node
    state = {"file_path": sample_csv, "cleaned_path": str("src/testreports/cleaned.csv")}
    result = data_cleaning_node(state)

    # Step 2: Load cleaned data
    cleaned_df = pd.read_csv(result["cleaned_file"])

    # Step 3: Save cleaned data to file for inspection
    cleaned_output_path = "src/testreports/cleaned_output.csv"
    cleaned_df.to_csv(cleaned_output_path, index=False)

    # Step 4: Assertions
    assert cleaned_df.isnull().sum().sum() == 0  # no nulls remain
    assert os.path.exists(cleaned_output_path)
    assert "logs" in result
    assert "Null values imputed" in result["logs"][0]

    # Optional: also save JSON summary of cleaned state
    with open("src/testreports/cleaned_state.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
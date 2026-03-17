import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import json
from src.nodes.column_stats_node import column_stats_node
from src.nodes.unstructured_profile_node import unstructured_profile_node

def test_unstructured_profile_node(tmp_path):
    # Step 1: Get profiling summary from column_stats_node
    state = {"file_path": "src/data/sampletestfilecsv.csv"}
    profiling_state = column_stats_node(state)

    # Step 2: Pass that state into unstructured_profile_node
    result = unstructured_profile_node(profiling_state)

    # Step 3: Print and save results for inspection
    print(result)
    with open("unstructured_output.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    # Step 4: Assertions
    assert "inferred_schema" in result
    assert "id" in result["inferred_schema"]
    assert "age" in result["inferred_schema"]
    assert "logs" in result
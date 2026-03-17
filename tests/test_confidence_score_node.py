
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.nodes.confidence_score_node import confidence_node

import json
from src.nodes.column_stats_node import column_stats_node

def test_confidence_node_with_csv(tmp_path):
    # Step 1: Generate profiling summary from the sample CSV
    state = {"file_path": "src/data/sampletestfilecsv.csv"}
    profiling_state = column_stats_node(state)

    # Step 2: Pass that into confidence_node
    result = confidence_node(profiling_state)

    # Step 3: Save and inspect
    with open("confidence_score.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    # Step 4: Assertions
    assert "confidence_score" in result
    assert isinstance(result["confidence_score"], float)
    assert "logs" in result
    assert "Confidence score computed." in result["logs"]
import sys, os, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.nodes.column_stats_node import column_stats_node
from src.nodes.quality_rules_node import rules_node

def test_rules_node_with_csv(tmp_path):
    # Step 1: Generate profiling summary from the sample CSV
    state = {"file_path": "src/data/sampletestfilecsv.csv"}
    profiling_state = column_stats_node(state)

    # Step 2: Pass that into rules_node
    result = rules_node(profiling_state)

    # Step 3: Save result for inspection
    with open("quality_rules.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    # Step 4: Assertions
    assert "quality_rules" in result
    assert isinstance(result["quality_rules"], list)
    assert any("must not contain nulls" in rule for rule in result["quality_rules"])
    assert "logs" in result
    assert "Quality rules inferred." in result["logs"]
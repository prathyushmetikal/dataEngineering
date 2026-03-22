import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import json

from src.nodes.profiling_report_node import report_node

def test_report_node():
    state = {"file_path": "src/data/sampletestfilecsv.csv"}
    result = report_node(state)
    print(result)
    with open("profiling_report.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    assert "report_path" in result
    assert result["report_path"].endswith(".html")
    assert "Profiling report generated." in result["logs"]
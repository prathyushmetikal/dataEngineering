import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import json
import pandas as pd
from src.nodes.column_stats_node import column_stats_node

def test_column_stats_node():
    state = {"file_path": "src/data/patientdatasample.csv"}
    result = column_stats_node(state)
    print(result)   # <-- this will show the full dictionary in pytest output
    with open("patient_statistics.json", "w") as f:
        json.dump(result, f, indent=2,default=str)

    assert "profiling_summary" in result
    assert "logs" in result
    assert "age" in result["profiling_summary"]


# pytest tests/test_column_stats_node.py -v
# >>
# ================================================ test session starts ================================================
# platform win32 -- Python 3.12.13, pytest-9.0.2, pluggy-1.6.0 -- E:\HexawareGENAIProjects\DataProfilingAgent\.venv\Scripts\python.exe
# cachedir: .pytest_cache
# rootdir: E:\HexawareGENAIProjects\DataProfilingAgent
# configfile: pyproject.toml
# plugins: anyio-4.12.1
# collected 1 item

# tests/test_column_stats_node.py::test_column_stats_node PASSED                                                 [100%]

# ================================================= 1 passed in 0.47s ================================================= 
# (dataprofilingagent) PS E:\HexawareGENAIProjects\DataProfilingAgent> 
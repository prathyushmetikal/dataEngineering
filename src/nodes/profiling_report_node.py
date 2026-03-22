# import pandas as pd
# from src.tools.profiling_report_tool import generate_profiling_report

# def report_node(state: dict) -> dict:
#     """
#     Node that generates a profiling report using ydata_profiling.
#     Expects state["file_path"] to point to the dataset.
#     """
#     file_path = state.get("file_path")
#     df = pd.read_csv(file_path)
#     print("before")
#     print(df)
#     print("after")
#     output_path = "profiling_report.html"
#     report_info = generate_profiling_report(df, output_path)

#     return {
#         **state,
#         "report_path": report_info["report_path"],
        
#         "logs": state.get("logs", []) + ["Profiling report generated."]
#     }

import pandas as pd
import json
from src.tools.profiling_report_tool import generate_profiling_report

def report_node(state: dict) -> dict:
    """
    Node that generates a profiling report using ydata_profiling.
    Expects state["file_path"] to point to the dataset.
    Also merges baseline YAML rules and LLM recommendations into the report.
    """
    file_path = state.get("file_path")
    df = pd.read_csv(file_path)

    # Generate profiling report HTML
    output_path = "profiling_report.html"
    report_info = generate_profiling_report(df, output_path)

    # Merge rules and recommendations
    rules = state.get("rules", {})
    merged_rules = {
        "baseline_rules": rules.get("baseline_rules", {}),
        "llm_recommendations": rules.get("llm_recommendations", [])
    }

    # Build JSON report structure
    profiling_summary = {
        "schema": state.get("inferred_schema"),
        "llm_analysis": state.get("llm_analysis"),
        "rules": merged_rules,
        "logs": state.get("logs", []) + ["Profiling report generated."]
    }

    # Save JSON alongside HTML
    with open("profiling_report.json", "w") as f:
        json.dump(profiling_summary, f, indent=2, default=str)

    return {
        **state,
        "report_path": report_info["report_path"],   # HTML report
        "report_json": "profiling_report.json",      # JSON report path
        "logs": profiling_summary["logs"]
    }


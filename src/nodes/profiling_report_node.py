import pandas as pd
from src.tools.profiling_report_tool import generate_profiling_report

def report_node(state: dict) -> dict:
    """
    Node that generates a profiling report using ydata_profiling.
    Expects state["file_path"] to point to the dataset.
    """
    file_path = state.get("file_path")
    df = pd.read_csv(file_path)

    output_path = "profiling_report.html"
    report_info = generate_profiling_report(df, output_path)

    return {
        **state,
        "report_path": report_info["report_path"],
        
        "logs": state.get("logs", []) + ["Profiling report generated."]
    }
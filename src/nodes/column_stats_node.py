import pandas as pd
from src.tools.column_stats_tool import generate_column_stats

def column_stats_node(state: dict) -> dict:
    """
    Node that generates column statistics using the tool.
    Expects state["file_path"] to point to the dataset.
    """
    df = pd.read_csv(state["file_path"])
    stats = generate_column_stats(df)

    # Ensure logs is always a list
    logs = state.get("logs", [])
    if not isinstance(logs, list):
        logs = [str(logs)]  # wrap string or other type into a list

    logs.append("Column stats generated.")

    return {
        **state,
        "profiling_summary": stats,
        "logs": logs
    }
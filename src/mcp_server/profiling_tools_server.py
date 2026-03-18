import time
import numpy as np
import pandas as pd
from src.nodes.column_stats_node import column_stats_node
from src.nodes.unstructured_profile_node import unstructured_profile_node
from src.nodes.profiling_report_node import report_node
from src.nodes.confidence_score_node import confidence_node
from src.nodes.quality_rules_node import rules_node

TOOLS_REGISTRY = {
    "generate_column_stats": column_stats_node,
    "profile_unstructured": unstructured_profile_node,
    "generate_report": report_node,
    "compute_confidence": confidence_node,
    "infer_rules": rules_node,
}

def to_python(obj):
    """
    Recursively convert NumPy/Pandas objects into plain Python types
    so FastAPI can serialize them to JSON.
    """
    if isinstance(obj, np.generic):  # numpy.int64, numpy.float64, etc.
        return obj.item()
    if isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, dict):
        return {k: to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_python(v) for v in obj]
    return obj

def handle_request(tool_name: str, state: dict):
    if tool_name not in TOOLS_REGISTRY:
        return {"error": f"Tool {tool_name} not found"}

    tool_fn = TOOLS_REGISTRY[tool_name]

    start_time = time.perf_counter()
    result = tool_fn(state)
    end_time = time.perf_counter()

    elapsed = round(end_time - start_time, 4)

    # Sanitize the result before attaching benchmark info
    result = to_python(result)

    # Ensure result is always a dict
    if not isinstance(result, dict):
        result = {"result": result}

    # Attach benchmark info
    result["benchmark"] = {
        "tool": tool_name,
        "elapsed_seconds": elapsed
    }

    return result
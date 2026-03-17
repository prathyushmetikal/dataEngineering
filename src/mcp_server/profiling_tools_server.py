import time
from nodes.column_stats_node import column_stats_node
from nodes.unstructured_profile_node import unstructured_profile_node
from nodes.profiling_report_node import report_node
from nodes.confidence_score_node import confidence_node
from nodes.quality_rules_node import rules_node

TOOLS_REGISTRY = {
    "generate_column_stats": column_stats_node,
    "profile_unstructured": unstructured_profile_node,
    "generate_report": report_node,
    "compute_confidence": confidence_node,
    "infer_rules": rules_node,
}

def handle_request(tool_name: str, state: dict):
    if tool_name not in TOOLS_REGISTRY:
        return {"error": f"Tool {tool_name} not found"}

    tool_fn = TOOLS_REGISTRY[tool_name]

    start_time = time.perf_counter()
    result = tool_fn(state)
    end_time = time.perf_counter()

    elapsed = round(end_time - start_time, 4)

    # Attach benchmark info to result
    result["benchmark"] = {
        "tool": tool_name,
        "elapsed_seconds": elapsed
    }
    return result
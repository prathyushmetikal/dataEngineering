def unstructured_profile_node(state: dict) -> dict:
    """
    Node that infers schema from profiling_summary.
    Expects state["profiling_summary"] from column_stats_node.
    """
    profiling_summary = state.get("profiling_summary", {})
    schema = {}

    for col, stats in profiling_summary.items():
        schema[col] = {
            "nulls": type(stats.get("nulls")).__name__,
            "unique": type(stats.get("unique")).__name__,
            "min": type(stats.get("min")).__name__,
            "max": type(stats.get("max")).__name__,
            "std_dev": type(stats.get("std_dev")).__name__,
            "distribution": type(stats.get("distribution")).__name__,
        }

    return {
        **state, 
        #"file_path": state["file_path"], 
        "inferred_schema": schema,
        "logs": state.get("logs", []) + ["Schema inferred from profiling summary."]
    }
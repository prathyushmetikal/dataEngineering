def unstructured_profile_node(state: dict) -> dict:
    """
    Node that infers schema from profiling_summary.
    Expects state["profiling_summary"] from column_stats_node.
    """
    profiling_summary = state.get("profiling_summary", {})
    schema = {}

    for col, stats in profiling_summary.items():
        # schema[col] = {
        #     "nulls": type(stats.get("nulls")).__name__,
        #     "unique": type(stats.get("unique")).__name__,
        #     "min": type(stats.get("min")).__name__,
        #     "max": type(stats.get("max")).__name__,
        #     "std_dev": type(stats.get("std_dev")).__name__,
        #     "distribution": type(stats.get("distribution")).__name__,
        # }
        # schema[col] = {
        #     "nulls": type(stats.get("nulls")).__name__,
        #     "unique": type(stats.get("unique")).__name__,
        #     "min": type(stats.get("min")).__name__,
        #     "max": type(stats.get("max")).__name__,
        #     "std_dev": type(stats.get("std_dev")).__name__,
        #     "distribution": type(stats.get("distribution")).__name__,
        # }

        schema[col] = {
            "nulls": stats.get("nulls"),        # ← actual value, not type().__name__
            "unique": stats.get("unique"),
            "min": stats.get("min"),
            "max": stats.get("max"),
            "std_dev": stats.get("std_dev"),
        }

    return {
        **state, 
        #"file_path": state["file_path"], 
        "inferred_schema": schema,
        "logs": state.get("logs", []) + ["Schema inferred from profiling summary."]
    }
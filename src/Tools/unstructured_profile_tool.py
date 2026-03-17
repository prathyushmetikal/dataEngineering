import json

def profile_unstructured(state: dict) -> dict:
    try:
        profiling_summary = state.get("profiling_summary", {})
        schema = {}
        for col, stats in profiling_summary.items():
            # Infer schema based on the stats dict
            schema[col] = {
                "nulls": type(stats.get("nulls")).__name__,
                "unique": type(stats.get("unique")).__name__,
                "min": type(stats.get("min")).__name__,
                "max": type(stats.get("max")).__name__,
                "std_dev": type(stats.get("std_dev")).__name__,
                "distribution": type(stats.get("distribution")).__name__,
            }
        return {"inferred_schema": schema}
    except Exception as e:
        return {"error": f"Could not infer schema: {e}"}

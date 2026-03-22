from src.tools.quality_rules_tool import infer_quality_rules

def rules_node(state: dict):
    """
    Node that infers data quality rules from profiling stats.
    Expects state["profiling_summary"] to contain column stats.
    """
    stats = state.get("profiling_summary", {})
    rules = infer_quality_rules(stats)
    return {
        **state, 
        #"file_path": state["file_path"], 
        "quality_rules": rules,
        #"logs": ["Quality rules inferred."]
        "logs": state.get("logs", []) + ["Quality rules inferred."]
    }
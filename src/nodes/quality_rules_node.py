from Tools.quality_rules_tool import infer_quality_rules

def rules_node(state: dict):
    """
    Node that infers data quality rules from profiling stats.
    Expects state["profiling_summary"] to contain column stats.
    """
    stats = state.get("profiling_summary", {})
    rules = infer_quality_rules(stats)
    return {
        "quality_rules": rules,
        "logs": ["Quality rules inferred."]
    }
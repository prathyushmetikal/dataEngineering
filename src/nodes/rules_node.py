from src.tools.rules_tool import validate_rules

def rules_node(state: dict) -> dict:
    """
    Node wrapper for rules validation.
    Consumes llm_analysis from state and merges with YAML rules.
    """
    llm_analysis = state.get("llm_analysis", {})
    merged_rules = validate_rules(llm_analysis)

    return {
        **state,
        "rules": merged_rules,
        "logs": state.get("logs", []) + ["Rules validated with YAML + LLM recommendations."]
    }
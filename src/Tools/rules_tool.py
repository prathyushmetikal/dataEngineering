import yaml

def validate_rules(llm_analysis: dict, rules_file: str = "rules.yaml") -> dict:
    """
    Core logic for rules validation.
    - Loads baseline rules from YAML.
    - Merges with LLM recommendations.
    Returns a dictionary with baseline rules and LLM recommendations.
    """
    with open(rules_file, "r") as f:
        yaml_rules = yaml.safe_load(f)

    # Handle both styles: either top-level "rules" or direct dict
    if "rules" in yaml_rules:
        baseline_rules = yaml_rules["rules"]
    else:
        baseline_rules = yaml_rules  # assume rules defined directly at root

    llm_recommendations = llm_analysis.get("recommendations", [])

    merged_rules = {
        "baseline_rules": baseline_rules,
        "llm_recommendations": llm_recommendations
    }
    return merged_rules
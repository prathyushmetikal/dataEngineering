def infer_quality_rules(stats: dict) -> list:
    rules = []
    for col, v in stats.items():
        if v["nulls"] == 0:
            rules.append(f"{col} must not contain nulls")
        if v["unique"] == len(v["distribution"]):
            rules.append(f"{col} values must be unique")
    return rules
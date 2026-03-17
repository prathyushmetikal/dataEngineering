def compute_confidence_score(stats: dict) -> float:
    total_columns = len(stats)
    
    # Convert nulls to int safely
    nulls = sum(int(v.get("nulls", 0)) for v in stats.values())
    completeness = 1 - (nulls / total_columns)

    # Convert uniques to int safely
    uniques = sum(int(v.get("unique", 0)) for v in stats.values())
    uniqueness = uniques / total_columns

    score = (completeness + uniqueness) / 2
    return round(score, 2)
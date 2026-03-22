# def compute_confidence_score(stats: dict) -> float:
#     total_columns = len(stats)
    
#     # Convert nulls to int safely
#     nulls = sum(int(v.get("nulls", 0)) for v in stats.values())
#     completeness = 1 - (nulls / total_columns)

#     # Convert uniques to int safely
#     uniques = sum(int(v.get("unique", 0)) for v in stats.values())
#     uniqueness = uniques / total_columns

#     score = (completeness + uniqueness) / 2
#     return round(score, 2)

def compute_confidence_score(stats: dict) -> float:
    if not stats:
        return 0.0
    total_columns = len(stats)
    total_nulls = sum(v.get("nulls", 0) for v in stats.values() if isinstance(v, dict))
    completeness = 1 - (total_nulls / (total_columns * 100))  # rough estimate
    return round(max(0.0, min(1.0, completeness)), 2)
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

def compute_confidence_score(stats):
    total_columns = stats.get("total_columns", 0)
    nulls = stats.get("nulls", 0)

    if total_columns == 0:
        return 0.0  # or some default baseline

    completeness = 1 - (nulls / total_columns)
    # add other factors here
    return completeness
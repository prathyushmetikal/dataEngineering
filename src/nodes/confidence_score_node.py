from src.tools.confidence_score_tool import compute_confidence_score

def confidence_node(state: dict):
    """
    Node that computes a synthetic confidence score for dataset quality.
    Expects state["profiling_summary"] to contain column stats.
    """
    stats = state.get("profiling_summary", {})
    score = compute_confidence_score(stats)
    return {
        "confidence_score": score,
        "logs": ["Confidence score computed."]
    }
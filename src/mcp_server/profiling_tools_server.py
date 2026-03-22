import time
import numpy as np
import pandas as pd
import math
from src.nodes.column_stats_node import column_stats_node
from src.nodes.unstructured_profile_node import unstructured_profile_node
from src.nodes.profiling_report_node import report_node
from src.nodes.confidence_score_node import confidence_node
from src.nodes.quality_rules_node import rules_node
from src.nodes.data_cleaning_node import data_cleaning_node
from src.nodes.llm_analysis_node import llm_analysis_node

# ── Tool registry (mirrors the graph nodes exactly) ──────────────────────────
TOOLS_REGISTRY = {
    # Step 1 — always runs first
    "generate_column_stats": column_stats_node,

    # Step 2a — conditional: runs only when nulls detected (max 2 passes)
    "clean_data": data_cleaning_node,

    # Step 2b — runs after stats are clean
    "profile_unstructured": unstructured_profile_node,

    # Step 3 — LLM analysis of inferred schema
    "run_llm_analysis": llm_analysis_node,

    # Step 4 — rules validation (YAML + LLM recommendations)
    "infer_rules": rules_node,

    # Step 5 — profiling report (HTML + JSON)
    "generate_report": report_node,

    # Step 6 — confidence score
    "compute_confidence": confidence_node,
}

# ── Execution order for reference / orchestration ────────────────────────────
PIPELINE_ORDER = [
    "generate_column_stats",   # → conditional: nulls? → clean_data (loop ≤2) or profile_unstructured
    "clean_data",              # → back to generate_column_stats (max 2 iterations)
    "profile_unstructured",    # → run_llm_analysis
    "run_llm_analysis",        # → infer_rules
    "infer_rules",             # → generate_report
    "generate_report",         # → compute_confidence
    "compute_confidence",      # → END
]

# ── Tool metadata (for MCP tool-listing endpoint) ────────────────────────────
TOOLS_METADATA = {
    "generate_column_stats": {
        "description": "Generates per-column statistics (nulls, unique, min, max, std_dev, distribution).",
        "requires": ["file_path"],
        "produces": ["profiling_summary"],
    },
    "clean_data": {
        "description": "Imputes nulls: mean for numeric, mode for categorical, median for datetime. Runs max 2 passes.",
        "requires": ["file_path"],
        "produces": ["cleaned_file", "file_path", "cleaning_iterations"],
    },
    "profile_unstructured": {
        "description": "Infers schema types from profiling_summary.",
        "requires": ["profiling_summary"],
        "produces": ["inferred_schema"],
    },
    "run_llm_analysis": {
        "description": "Sends inferred schema to LLM; detects quality issues and returns recommendations.",
        "requires": ["inferred_schema"],
        "produces": ["llm_analysis"],
    },
    "infer_rules": {
        "description": "Merges YAML baseline rules with LLM recommendations into a unified rules dict.",
        "requires": ["llm_analysis"],
        "produces": ["rules"],
    },
    "generate_report": {
        "description": "Generates profiling report as HTML and JSON, merging schema, analysis, and rules.",
        "requires": ["file_path", "inferred_schema", "llm_analysis", "rules"],
        "produces": ["report_path", "report_json"],
    },
    "compute_confidence": {
        "description": "Computes a 0–1 confidence score based on null rates across columns.",
        "requires": ["profiling_summary"],
        "produces": ["confidence_score"],
    },
}

# ── Serialization helper ──────────────────────────────────────────────────────
# def to_python(obj):
#     """
#     Recursively convert NumPy/Pandas objects into plain Python types
#     so FastAPI can serialize them to JSON.
#     """
#     if isinstance(obj, np.generic):
#         return obj.item()
#     if isinstance(obj, (np.ndarray, pd.Series)):
#         return obj.tolist()
#     if isinstance(obj, pd.DataFrame):
#         return obj.to_dict(orient="records")
#     if isinstance(obj, dict):
#         return {k: to_python(v) for k, v in obj.items()}
#     if isinstance(obj, (list, tuple, set)):
#         return [to_python(v) for v in obj]
#     return obj

def to_python(obj):
    """
    Recursively convert NumPy/Pandas objects into plain Python types
    so FastAPI can serialize them to JSON.
    """
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None                          # ← convert nan/inf to None (JSON null)

    if isinstance(obj, np.generic):
        val = obj.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None                      # ← handle numpy nan too
        return val

    if isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()

    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")

    if isinstance(obj, dict):
        return {
            (None if (isinstance(k, float) and math.isnan(k)) else k): to_python(v)
            for k, v in obj.items()          # ← handle nan KEYS in distribution dict
        }

    if isinstance(obj, (list, tuple, set)):
        return [to_python(v) for v in obj]

    return obj

# ── Request handler ───────────────────────────────────────────────────────────
def handle_request(tool_name: str, state: dict):
    """
    Executes a single tool by name and returns its output with benchmark info.
    Use build_agent() in app.py to run the full pipeline instead.
    """
    if tool_name not in TOOLS_REGISTRY:
        return {
            "error": f"Tool '{tool_name}' not found.",
            "available_tools": list(TOOLS_REGISTRY.keys())
        }

    # Validate required state keys
    required_keys = TOOLS_METADATA.get(tool_name, {}).get("requires", [])
    missing = [k for k in required_keys if k not in state]
    if missing:
        return {
            "error": f"Tool '{tool_name}' is missing required state keys: {missing}",
            "required": required_keys,
        }

    tool_fn = TOOLS_REGISTRY[tool_name]

    start_time = time.perf_counter()
    try:
        result = tool_fn(state)
    except Exception as e:
        return {
            "error": f"Tool '{tool_name}' raised an exception: {str(e)}",
            "tool": tool_name,
        }
    elapsed = round(time.perf_counter() - start_time, 4)

    # Sanitize for JSON serialization
    result = to_python(result)

    if not isinstance(result, dict):
        result = {"result": result}

    # Attach benchmark info
    result["benchmark"] = {
        "tool": tool_name,
        "elapsed_seconds": elapsed,
        "produces": TOOLS_METADATA.get(tool_name, {}).get("produces", []),
    }

    return result

# ── Tool listing helper (for MCP /tools endpoint) ────────────────────────────
def list_tools():
    """Returns all registered tools with their metadata."""
    return [
        {
            "name": name,
            **TOOLS_METADATA.get(name, {}),
        }
        for name in PIPELINE_ORDER
        if name in TOOLS_REGISTRY
    ]
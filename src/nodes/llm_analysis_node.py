# src/nodes/llm_analysis_node.py
import json
from src.llm_client import call_llm

def llm_analysis_node(state: dict) -> dict:
    schema = state.get("inferred_schema", {})
    prompt = f"""
    You are a data quality analyst. Given this inferred schema:
    {schema}
    Identify if there are data quality issues (nulls, outliers, invalid values).
    Respond with JSON:
    {{
      "issues_found": true/false,
      "issues": ["list of problems"],
      "recommendations": ["list of fixes"]
    }}
    """
    llm_response = call_llm(prompt, model="qwen2:1.5b")

    try:
        analysis = json.loads(llm_response)
    except Exception:
        analysis = {"issues_found": False, "issues": [], "recommendations": []}

    # ← REMOVED: data_cleaning_node call
    # Reason: cleaning is already handled by the graph via has_nulls conditional
    # before llm_analysis_node is ever reached. Calling it again here:
    #   1. triggers a 3rd cleaning pass outside the graph's control
    #   2. increments cleaning_iterations unexpectedly
    #   3. bypasses the recursion limit safety net

    return {
        **state,
        "llm_analysis": analysis,
        "logs": state.get("logs", []) + [
            "LLM found issues, flagged for review."
            if analysis.get("issues_found")
            else "LLM found no issues."
        ]
    }
# ```

# The key reason is **separation of concerns** in the graph:
# ```
# # Graph already handles cleaning BEFORE llm_analysis runs:

# column_stats → has_nulls? 
#                   ↓ True              ↓ False
#                cleaning          unstructured
#                   ↓                    ↓
#             column_stats          llm_analysis  ← arrives here already clean
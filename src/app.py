# from langgraph.graph import StateGraph, END
# from src.nodes.column_stats_node import column_stats_node
# from src.nodes.unstructured_profile_node import unstructured_profile_node
# from src.nodes.profiling_report_node import report_node
# from src.nodes.confidence_score_node import confidence_node
# from src.nodes.quality_rules_node import rules_node
# from src.nodes.data_cleaning_node import data_cleaning_node
# from src.nodes.llm_analysis_node import llm_analysis_node

# # # Utility function to check nulls
# # def has_nulls(state: dict) -> bool:
# #     profiling_summary = state.get("profiling_summary", {})
# #     for col, stats in profiling_summary.items():
# #         if stats.get("nulls", 0) > 0:
# #             return True
# #     return False

# # def has_nulls(state: dict) -> bool:
# #     if state.get("cleaning_done"):   # ← add this block at the top
# #         return False
    
# #     profiling_summary = state.get("profiling_summary", {})
# #     for col, stats in profiling_summary.items():
# #         # Ensure stats is a dict before calling .get
# #         if isinstance(stats, dict):
# #             if stats.get("nulls", 0) > 0:
# #                 return True
# #         # If stats is not a dict, handle gracefully
# #         elif isinstance(stats, (int, float)):
# #             if stats > 0:  # assume it's a null count
# #                 return True
# #     return False

# def has_nulls(state: dict) -> bool:
#     if state.get("cleaning_iterations", 0) >= 2:   # ← allow max 2 cleaning passes
#         return False

#     profiling_summary = state.get("profiling_summary", {})
#     for col, stats in profiling_summary.items():
#         if isinstance(stats, dict):
#             if stats.get("nulls", 0) > 0:
#                 return True
#         elif isinstance(stats, (int, float)):
#             if stats > 0:
#                 return True
#     return False


# def build_agent():
#     builder = StateGraph(dict)

#     # Nodes
#     builder.add_node("column_stats", column_stats_node)
#     builder.add_node("cleaning", data_cleaning_node)
#     builder.add_node("unstructured", unstructured_profile_node)
#     builder.add_node("llm_analysis", llm_analysis_node)
#     builder.add_node("report", report_node)
#     builder.add_node("confidence", confidence_node)
#     builder.add_node("rules", rules_node)

#     # Entry point
#     builder.set_entry_point("column_stats")

#     # First conditional: after initial stats
#     builder.add_conditional_edges(
#         "column_stats",
#         has_nulls,
#         {True: "cleaning", False: "unstructured"}
#     )

#     # After cleaning, run column_stats again
#     builder.add_edge("cleaning", "column_stats")

#         # After unstructured schema inference
#     builder.add_edge("unstructured", "llm_analysis")

#     # Then continue to report, confidence, rules...
#     #builder.add_edge("llm_analysis", "report")
#     builder.add_edge("llm_analysis", "rules")
#     builder.add_edge("rules", "report")



#     # Continue pipeline
#     #builder.add_edge("unstructured", "report")
#     builder.add_edge("report", "confidence")
#     builder.add_edge("confidence", END)
#     #builder.add_edge("rules", END)

#     return builder.compile()
    
# if __name__=='__main__':
#     react_graph = build_agent()

#     # Initial state: pass in your CSV file path
    
#     initial_state = {"file_path": r"E:\HexawareGENAIProjects\DataProfilingAgent\src\data\patientdatasample.csv"}
#     #initial_state = {"file_path": "src/data/sampletestfilecsv.csv"}

#     # Run the graph
#     final_state = react_graph.invoke(initial_state,config={"recursion_limit": 20})

#     # Print key outputs only (not the full state which is very long)
#     print("\n=== PIPELINE COMPLETE ===")
#     print(f"Logs:             {final_state.get('logs')}")
#     print(f"Confidence Score: {final_state.get('confidence_score')}")
#     print(f"Report HTML:      {final_state.get('report_path')}")
#     print(f"Report JSON:      {final_state.get('report_json')}")
#     print(f"Cleaning Passes:  {final_state.get('cleaning_iterations', 0)}")
#     print(f"Quality Rules:    {final_state.get('quality_rules')}")
#     print(f"LLM Analysis:     {final_state.get('llm_analysis')}")
#     # # Optionally draw the graph
#     # react_graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
#     # ← REPLACE draw_mermaid_png with this
#     try:
#         mermaid_text = react_graph.get_graph().draw_mermaid()
#         with open("graph.md", "w") as f:
#             f.write(f"```mermaid\n{mermaid_text}\n```")
#         print("Graph saved to graph.md")
#     except Exception as e:
#         print(f"Could not draw graph: {e}")

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from src.nodes.column_stats_node import column_stats_node
from src.nodes.unstructured_profile_node import unstructured_profile_node
from src.nodes.profiling_report_node import report_node
from src.nodes.confidence_score_node import confidence_node
from src.nodes.quality_rules_node import rules_node
from src.nodes.data_cleaning_node import data_cleaning_node
from src.nodes.llm_analysis_node import llm_analysis_node

# ← ADD THIS
class AgentState(TypedDict, total=False):
    file_path: str
    profiling_summary: dict
    inferred_schema: dict
    llm_analysis: dict
    rules: dict
    quality_rules: list
    report_path: str
    report_json: str
    confidence_score: float
    cleaned_file: str
    cleaned_path: str
    cleaning_iterations: int
    cleaning_done: bool
    logs: list

def has_nulls(state: AgentState) -> bool:
    if state.get("cleaning_iterations", 0) >= 2:
        return False
    profiling_summary = state.get("profiling_summary", {})
    for col, stats in profiling_summary.items():
        if isinstance(stats, dict):
            if stats.get("nulls", 0) > 0:
                return True
        elif isinstance(stats, (int, float)):
            if stats > 0:
                return True
    return False

def build_agent():
    builder = StateGraph(AgentState)  # ← USE AgentState instead of dict

    builder.add_node("column_stats", column_stats_node)
    builder.add_node("cleaning", data_cleaning_node)
    builder.add_node("unstructured", unstructured_profile_node)
    builder.add_node("llm_analysis", llm_analysis_node)
    builder.add_node("report", report_node)
    builder.add_node("confidence", confidence_node)
    builder.add_node("rules", rules_node)

    builder.set_entry_point("column_stats")

    builder.add_conditional_edges(
        "column_stats",
        has_nulls,
        {True: "cleaning", False: "unstructured"}
    )

    builder.add_edge("cleaning", "column_stats")
    builder.add_edge("unstructured", "llm_analysis")
    builder.add_edge("llm_analysis", "rules")
    builder.add_edge("rules", "report")
    builder.add_edge("report", "confidence")
    builder.add_edge("confidence", END)

    return builder.compile()

if __name__ == '__main__':
    react_graph = build_agent()

    initial_state = {
        "file_path": r"E:\HexawareGENAIProjects\DataProfilingAgent\src\data\patientdatasample.csv"
    }

    final_state = react_graph.invoke(
        initial_state,
        config={"recursion_limit": 25}
    )

    print("\n=== PIPELINE COMPLETE ===")
    print(f"Logs:             {final_state.get('logs')}")
    print(f"Confidence Score: {final_state.get('confidence_score')}")
    print(f"Report HTML:      {final_state.get('report_path')}")
    print(f"Report JSON:      {final_state.get('report_json')}")
    print(f"Cleaning Passes:  {final_state.get('cleaning_iterations', 0)}")
    print(f"LLM Analysis:     {final_state.get('llm_analysis')}")

    # ← NOW this will work
    try:
        react_graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        print("Graph saved to graph.png")
    except Exception as e:
        print(f"Could not draw graph: {e}")
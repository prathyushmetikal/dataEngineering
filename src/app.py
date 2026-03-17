from langgraph.graph import StateGraph, END
from nodes.column_stats_node import column_stats_node
from nodes.unstructured_profile_node import unstructured_profile_node
from nodes.profiling_report_node import report_node
from nodes.confidence_score_node import confidence_node
from nodes.quality_rules_node import rules_node

def build_agent():
    builder = StateGraph(dict)

    builder.add_node("column_stats", column_stats_node)
    builder.add_node("unstructured", unstructured_profile_node)
    builder.add_node("report", report_node)
    builder.add_node("confidence", confidence_node)
    builder.add_node("rules", rules_node)

    builder.set_entry_point("column_stats")
    builder.add_edge("column_stats", "unstructured")
    builder.add_edge("unstructured", "report")
    builder.add_edge("report", "confidence")
    builder.add_edge("confidence", "rules")
    builder.add_edge("rules", END)

    return builder.compile()


    
if __name__=='__main__':
    react_graph=build_agent()
    react_graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
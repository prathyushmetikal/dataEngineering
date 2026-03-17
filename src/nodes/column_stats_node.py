import pandas as pd
from Tools.column_stats_tool import generate_column_stats

def column_stats_node(state: dict):
    state = {"file_path": "src/data/sampletestfilecsv.csv"}
    df = pd.read_csv(state["file_path"])
    stats = generate_column_stats(df)
    return {"profiling_summary": stats, "logs": ["Column stats generated."]}

    # df = pd.read_excel(state["file_path"])
    # stats = generate_column_stats(df)
    #return {"profiling_summary": stats, "logs": ["Column stats generated."]}

# import pandas as pd
# from Tools.column_stats_tool import generate_column_stats

# def column_stats_node(state: dict):
#     df = pd.read_excel(state["file_path"])
#     stats = generate_column_stats(df)
#     return {"profiling_summary": stats, "logs": ["Column stats generated."]}
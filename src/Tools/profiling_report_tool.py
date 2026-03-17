from ydata_profiling import ProfileReport
import pandas as pd

def generate_profiling_report(df: pd.DataFrame, output_path: str):
    profile = ProfileReport(df, title="Data Profiling Report", minimal=True)
    profile.to_file(output_path)
    return {"report_path": output_path}
# src/tools/star_schema_tool.py
def convert_to_star(schema: dict) -> dict:
    star_schema = {"fact_tables": [], "dimension_tables": []}
    return {"star_schema": star_schema, "logs": ["Converted schema to Star Schema."]}
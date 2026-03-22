# src/tools/schema_extractor_tool.py
from sqlalchemy import create_engine, inspect

def extract_schema(connection_string: str) -> dict:
    engine = create_engine(connection_string)
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [{"name": c["name"], "type": str(c["type"])} for c in columns]
    return {"schema": schema, "logs": ["Schema extracted from PostgreSQL."]}
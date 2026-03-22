# src/tools/normalize_3nf_tool.py

def normalize_to_3nf(schema: dict) -> dict:
    normalized_tables = {}
    relationships = []
    logs = []

    for table_name, columns in schema.items():
        main_columns = []
        lookup_tables = {}

        # Guard: columns might be a list of strings or list of dicts
        normalized_cols = []
        for col in columns:
            if isinstance(col, str):
                normalized_cols.append({"name": col, "type": "VARCHAR"})
            elif isinstance(col, dict):
                normalized_cols.append(col)
            else:
                continue  # skip unknown types

        # Find primary key
        pk_col = next(
            (c for c in normalized_cols if c.get("name", "").lower() in ("id", f"{table_name}_id")),
            normalized_cols[0] if normalized_cols else None
        )

        for col in normalized_cols:
            col_name = col.get("name", "").lower()        # ← safe .get()
            col_type = col.get("type", "VARCHAR").upper() # ← safe .get() with default

            # Categorical columns → extract to lookup table
            if any(keyword in col_name for keyword in [
                "status", "type", "category", "gender",
                "department", "provider", "diagnosis", "medication"
            ]):
                lookup_table_name = f"{col.get('name')}_lookup"
                lookup_tables[lookup_table_name] = [
                    {"name": f"{col.get('name')}_id", "type": "INTEGER", "constraint": "PRIMARY KEY"},
                    {"name": col.get("name"),          "type": col_type},
                ]
                main_columns.append({
                    "name": f"{col.get('name')}_id",
                    "type": "INTEGER",
                    "constraint": f"FOREIGN KEY REFERENCES {lookup_table_name}({col.get('name')}_id)"
                })
                relationships.append({
                    "from_table":   table_name,
                    "from_column":  f"{col.get('name')}_id",
                    "to_table":     lookup_table_name,
                    "to_column":    f"{col.get('name')}_id",
                })
                logs.append(f"Extracted '{col.get('name')}' into lookup table '{lookup_table_name}'.")
            else:
                main_columns.append(col)

        normalized_tables[table_name] = main_columns
        normalized_tables.update(lookup_tables)
        logs.append(f"Table '{table_name}' normalized to 3NF.")

    return {
        "normalized_tables": normalized_tables,
        "relationships":     relationships,
        "logs":              logs,
    }
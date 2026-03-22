# src/tools/llm_schema_advisor.py
def llm_schema_advisor(schema: dict, option: str, llm) -> dict:
    prompt = f"""
    Given this OLTP schema: {schema}
    Transform it into {option} form (3NF or Star Schema).
    Provide table definitions, relationships, and reasoning.
    """
    response = llm.invoke(prompt)
    return {"llm_recommendation": response, "logs": ["LLM provided schema advice."]}
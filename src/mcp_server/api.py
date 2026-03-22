# # from fastapi import FastAPI
# # from pydantic import BaseModel
# # from src.mcp_server.profiling_tools_server import handle_request

# # app = FastAPI(title="Profiling Tools MCP Server")

# # class ToolRequest(BaseModel):
# #     tool_name: str
# #     state: dict

# # @app.post("/invoke_tool")
# # async def invoke_tool(request: ToolRequest):
# #     result = handle_request(request.tool_name, request.state)
# #     return result

# # src/api.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# from src.mcp_server.profiling_tools_server import handle_request

# # Import your new tools
# from src.tools.postgre_schema_extractor import extract_schema
# from src.tools.normalize_3nf_tool import normalize_to_3nf
# from src.tools.star_schema_tool import convert_to_star
# from src.tools.llm_schema_advisor import llm_schema_advisor

# app = FastAPI(title="Profiling + Data Modelling MCP Server")

# # Existing profiling request model
# class ToolRequest(BaseModel):
#     tool_name: str
#     state: dict

# @app.post("/invoke_tool")
# async def invoke_tool(request: ToolRequest):
#     result = handle_request(request.tool_name, request.state)
#     return result


# # New request model for schema transformation
# class SchemaRequest(BaseModel):
#     connection_string: str = None   # optional, if you want to connect to Postgres
#     schema: dict = None             # optional, if you want to pass schema JSON directly
#     option: str                     # "3NF" or "Star"

# @app.post("/transform_schema")
# async def transform_schema(request: SchemaRequest):
#     # Either extract schema from Postgres or use provided JSON
#     if request.schema:
#         schema = request.schema
#         logs = ["Schema provided via request."]
#     else:
#         schema_info = extract_schema(request.connection_string)
#         schema = schema_info["schema"]
#         logs = schema_info["logs"]

#     # Transform based on option
#     if request.option.upper() == "3NF":
#         transformed = normalize_to_3nf(schema)
#     else:
#         transformed = convert_to_star(schema)

#     # LLM advisor (replace llm=None with your actual LLM client)
#     llm_output = llm_schema_advisor(schema, request.option, llm=None)

#     return {
#         "schema": transformed,
#         "llm": llm_output,
#         "logs": logs + transformed["logs"] + llm_output["logs"]
#     }

# src/api.py
import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.mcp_server.profiling_tools_server import handle_request, list_tools, to_python
from src.tools.postgre_schema_extractor import extract_schema
from src.tools.normalize_3nf_tool import normalize_to_3nf
from src.tools.star_schema_tool import convert_to_star
from src.tools.llm_schema_advisor import llm_schema_advisor
#from src.app import build_agent

app = FastAPI(
    title="Profiling + Data Modelling MCP Server",
    description="MCP server for data profiling, quality rules, LLM analysis, and schema transformation.",
    version="1.0.0",
)

# ← ADD CORS so React app can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "src/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# ── Request Models ────────────────────────────────────────────────────────────

class ToolRequest(BaseModel):
    tool_name: str
    state: dict

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "generate_column_stats",
                "state": {"file_path": "src/data/sample.csv"}
            }
        }

class SchemaRequest(BaseModel):
    connection_string: Optional[str] = None  # Postgres connection string
    input_schema: Optional[dict] = None            # or pass schema JSON directly
    option: str                              # "3NF" or "Star"

    class Config:
        json_schema_extra = {
            "example": {
                "schema": {"users": [{"name": "id", "type": "INTEGER"}]},
                "option": "3NF"
            }
        }

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Check if the server is running."""
    return {"status": "ok"}

# ── Tool Listing ──────────────────────────────────────────────────────────────

@app.get("/tools")
async def get_tools():
    """
    Returns all registered profiling tools in pipeline order,
    with their required inputs and produced outputs.
    """
    return {"tools": list_tools()}

# ── Profiling Pipeline Tool Invocation ───────────────────────────────────────

@app.post("/invoke_tool")
async def invoke_tool(request: ToolRequest):
    """
    Invoke a single profiling pipeline tool by name.
    Pass the current pipeline state in the request body.
    Tools must be called in pipeline order — each tool's output
    feeds into the next tool's state.

    Pipeline order:
      generate_column_stats → clean_data (if nulls) →
      profile_unstructured → run_llm_analysis →
      infer_rules → generate_report → compute_confidence
    """
    result = handle_request(request.tool_name, request.state)

    # handle_request returns {"error": ...} on failure — raise as HTTP 400
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)

    return result


from src.app import build_agent

# ── File Upload Only (saves file, returns saved path) ─────────────────────────
# @app.post("/upload_file")
# async def upload_file(file: UploadFile = File(...)):
#     """
#     Accepts a CSV file upload and saves it to the uploads directory.
#     Returns the saved file path to use in /run_pipeline.
#     """
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are supported.")

#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     return {
#         "status": "uploaded",
#         "filename": file.filename,
#         "saved_path": file_path,       # ← use this in /run_pipeline
#         "message": f"File saved. Now call /run_pipeline with file_path: '{file_path}'"
#     }


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a CSV file upload, saves it, and automatically
    runs the full LangGraph pipeline. No manual intervention needed.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Step 1 — Save the file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 2 — Automatically run the pipeline
    try:
        agent = build_agent()
        final_state = agent.invoke(
            {"file_path": file_path},
            config={"recursion_limit": 25}
        )
        final_state = to_python(final_state)

        return {
            "status":            "success",
            "filename":          file.filename,
            "saved_path":        file_path,
            "logs":              final_state.get("logs"),
            "confidence_score":  final_state.get("confidence_score"),
            "report_path":       final_state.get("report_path"),
            "report_json":       final_state.get("report_json"),
            "cleaning_passes":   final_state.get("cleaning_iterations", 0),
            "llm_analysis":      final_state.get("llm_analysis"),
            "quality_rules":     final_state.get("quality_rules"),
            "inferred_schema":   final_state.get("inferred_schema"),
            "profiling_summary": final_state.get("profiling_summary"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
# ```

# Now the flow is completely automatic:
# ```
# User uploads CSV
#       ↓
# File saved to src/data/uploads/
#       ↓
# Pipeline runs automatically
#       ↓
# Full results returned in one response

# ── Run Pipeline (local file path OR previously uploaded file) ────────────────
@app.post("/run_pipeline")
async def run_pipeline(request: dict):
    """
    Runs the full LangGraph pipeline.
    Pass file_path pointing to either:
      - A local file:    "src/data/patientdatasample.csv"
      - An uploaded file: "src/data/uploads/yourfile.csv"
    """
    file_path = request.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path is required.")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: '{file_path}'. Upload it first via /upload_file."
        )

    try:
        agent = build_agent()
        final_state = agent.invoke(
            {"file_path": file_path},
            config={"recursion_limit": 25}
        )
        final_state = to_python(final_state)

        return {
            "status":            "success",
            "file_path":         file_path,
            "logs":              final_state.get("logs"),
            "confidence_score":  final_state.get("confidence_score"),
            "report_path":       final_state.get("report_path"),
            "report_json":       final_state.get("report_json"),
            "cleaning_passes":   final_state.get("cleaning_iterations", 0),
            "llm_analysis":      final_state.get("llm_analysis"),
            "quality_rules":     final_state.get("quality_rules"),
            "inferred_schema":   final_state.get("inferred_schema"),
            "profiling_summary": final_state.get("profiling_summary"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ── Schema Transformation ─────────────────────────────────────────────────────
@app.post("/transform_schema")
async def transform_schema(request: SchemaRequest):
    """
    Transform a database schema into 3NF or Star Schema form.
    Either provide a 'connection_string' to extract from Postgres,
    or provide the 'input_schema' dict directly.
    """
    # Validate: must have one of connection_string or input_schema
    if not request.connection_string and not request.input_schema:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'connection_string' or 'input_schema' in the request body."
        )

    # Validate option value
    if request.option.upper() not in ("3NF", "STAR"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid option '{request.option}'. Must be '3NF' or 'Star'."
        )

    # Step 1 — get schema (from Postgres or request body)
    try:
        if request.input_schema:
            schema = request.input_schema
            logs = ["Schema provided via request body."]
        else:
            schema_info = extract_schema(request.connection_string)
            schema = schema_info["schema"]
            logs = schema_info["logs"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema extraction failed: {str(e)}")

    # Step 2 — transform schema
    try:
        if request.option.upper() == "3NF":
            transformed = normalize_to_3nf(schema)
        else:
            transformed = convert_to_star(schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema transformation failed: {str(e)}")

    # Step 3 — LLM advisor (non-critical, won't fail the request)
    try:
        llm_output = llm_schema_advisor(schema, request.option, llm=None)
    except Exception as e:
        llm_output = {
            "llm_recommendation": f"LLM unavailable: {str(e)}",
            "logs": ["LLM advisor skipped due to error."]
        }

    return {
        "option":             request.option.upper(),
        "transformed_schema": transformed.get("normalized_tables") or transformed.get("star_schema"),
        "relationships":      transformed.get("relationships", []),
        "llm_recommendation": llm_output.get("llm_recommendation"),
        "logs":               logs + transformed.get("logs", []) + llm_output.get("logs", []),
    }
# @app.post("/transform_schema")
# async def transform_schema(request: SchemaRequest):
#     """
#     Transform a database schema into 3NF or Star Schema form.
#     Either provide a 'connection_string' to extract from Postgres,
#     or provide the 'schema' dict directly.
#     """
#     # Validate: must have one of connection_string or schema
#     if not request.connection_string and not request.schema:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide either 'connection_string' or 'schema' in the request body."
#         )

#     # Validate option value
#     if request.option.upper() not in ("3NF", "STAR"):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid option '{request.option}'. Must be '3NF' or 'Star'."
#         )

#     # Step 1 — get schema (from Postgres or request body)
#     try:
#         if request.schema:
#             schema = request.schema
#             logs = ["Schema provided via request body."]
#         else:
#             schema_info = extract_schema(request.connection_string)
#             schema = schema_info["schema"]
#             logs = schema_info["logs"]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Schema extraction failed: {str(e)}")

#     # Step 2 — transform schema
#     try:
#         if request.option.upper() == "3NF":
#             transformed = normalize_to_3nf(schema)
#         else:
#             transformed = convert_to_star(schema)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Schema transformation failed: {str(e)}")

#     # Step 3 — LLM advisor
#     # Replace llm=None with your actual LLM client instance when ready
#     try:
#         llm_output = llm_schema_advisor(schema, request.option, llm=None)
#     except Exception as e:
#         # LLM advice is non-critical — log the error but don't fail the request
#         llm_output = {
#             "llm_recommendation": f"LLM unavailable: {str(e)}",
#             "logs": ["LLM advisor skipped due to error."]
#         }

#     # Safely merge logs (guard against missing "logs" keys)
#     combined_logs = (
#         logs
#         + transformed.get("logs", [])
#         + llm_output.get("logs", [])
#     )

#     return {
#     "option": request.option.upper(),
#     "transformed_schema": transformed.get("normalized_tables") or transformed.get("star_schema"),
#     "relationships": transformed.get("relationships", []),
#     "llm_recommendation": llm_output.get("llm_recommendation"),
#     "logs": logs + transformed.get("logs", []) + llm_output.get("logs", []),
#     }

    # return {
    #     "option": request.option.upper(),
    #     "transformed_schema": transformed,
    #     "llm_recommendation": llm_output.get("llm_recommendation"),
    #     "logs": combined_logs,
    # }
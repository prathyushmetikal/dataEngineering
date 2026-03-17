from fastapi import FastAPI, Request
from mcp_server.profiling_tools_server import handle_request

app = FastAPI(title="Profiling Tools MCP Server")

@app.post("/invoke_tool")
async def invoke_tool(request: Request):
    payload = await request.json()
    tool_name = payload.get("tool_name")
    state = payload.get("state", {})
    result = handle_request(tool_name, state)
    return result
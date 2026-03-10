from fastapi import APIRouter, Request
import json
from src.services.llm_service import run_llm

router = APIRouter()

TOOLS_PROMPT = """
You are an AI assistant controlling a traffic surveillance system.

You can call the following tools:

where_object(object_id)
frames(object_id)
details(object_id)
frame_lookup(object_id, frame)
fence_usage(fence_id)
gate_sequence(object_id)
clip(object_id)
gate_clip(object_id, frame, camera)

Respond ONLY in JSON format:

{
 "tool": "tool_name",
 "arguments": {}
}

Example:

User: Where did vehicle 432 appear?

Response:
{
 "tool": "where_object",
 "arguments": {"object_id":432}
}

Camera IDs must be numeric.

Example:
cam1 → 1
cam2 → 2

The clip tool only accepts:

clip(object_id)

Example:

{
 "tool": "clip",
 "arguments": {"object_id":432}
}
"""


def init_router(tool_executor):
    global execute_tool
    execute_tool = tool_executor


@router.post("/chat")
async def chat(request: Request):

    data = await request.json()

    query = data.get("query")

    llm_output = run_llm(query, TOOLS_PROMPT)

    try:

        tool_call = json.loads(llm_output)

        result = execute_tool(tool_call)

        return {
            "tool_used": tool_call["tool"],
            "result": result
        }

    except Exception:

        return {
            "llm_response": llm_output
        }
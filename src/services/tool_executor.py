from src.routers.object_router import where_object, frame_ranges, object_details, where_object_at_frame
from src.routers.fence_router import fence_usage
from src.routers.gate_router import gate_sequence, gate_clip
from src.routers.clip_router import get_object_clip

def execute_tool(tool_call):

    tool = tool_call["tool"]
    args = tool_call["arguments"]

    if tool == "where_object":
        return where_object(**args)

    if tool == "frames":
        return frame_ranges(**args)

    if tool == "details":
        return object_details(**args)

    if tool == "frame_lookup":
        return where_object_at_frame(**args)

    if tool == "fence_usage":
        return fence_usage(**args)

    if tool == "gate_sequence":
        return gate_sequence(**args)

    if tool == "clip":
        return get_object_clip(**args)

    if tool == "gate_clip":
        return gate_clip(**args)

    return {"error": "Unknown tool"}
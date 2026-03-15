from fastapi import APIRouter, HTTPException
from src.services.clip_service import generate_object_clip

router = APIRouter()

objects = None
fps = None


def init_router(data_objects, data_fps):
    global objects, fps
    objects = data_objects
    fps = data_fps


@router.get("/clip")
def get_object_clip(object_id: int):

    clip_path = generate_object_clip(object_id, objects, fps)

    if clip_path is None:
        raise HTTPException(status_code=404, detail="Object not found")

    return {
        "type": "video_clip",
        "object_id": object_id,
        "clip_url": f"/{clip_path}",
        "playable": True
    }
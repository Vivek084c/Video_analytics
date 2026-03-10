from fastapi import APIRouter, HTTPException
from src.utils.segment_utils import get_segments

router = APIRouter()

# These will be initialized from app.py
objects = None
fps = None


def init_router(data_objects, data_fps):
    global objects, fps
    objects = data_objects
    fps = data_fps


@router.get("/where")
def where_object(object_id: int):

    obj_id = str(object_id)

    segments = get_segments(obj_id)

    if segments is None:
        raise HTTPException(status_code=404, detail="Object not found")

    appearances = []

    for seg in segments:
        appearances.append({
            "camera_id": seg["camera_id"],
            "start_frame": seg["start_frame"],
            "end_frame": seg["end_frame"]
        })

    return {
        "object_id": object_id,
        "appearances": appearances
    }


@router.get("/frames")
def frame_ranges(object_id: int):

    obj_id = str(object_id)

    segments = get_segments(obj_id)

    if segments is None:
        raise HTTPException(status_code=404, detail="Object not found")

    return {
        "object_id": object_id,
        "segments": segments
    }

@router.get("/details")
def object_details(object_id: int):

    obj_id = str(object_id)

    segments = get_segments(obj_id)

    if segments is None:
        raise HTTPException(status_code=404, detail="Object not found")

    cameras = set()
    total_frames = 0

    for seg in segments:
        cameras.add(seg["camera_id"])
        total_frames += seg["end_frame"] - seg["start_frame"] + 1

    duration_seconds = total_frames / fps

    return {
        "object_id": object_id,
        "cameras_seen": list(cameras),
        "total_segments": len(segments),
        "total_frames_visible": total_frames,
        "duration_seconds": round(duration_seconds, 2)
    }

@router.get("/frame_lookup")
def where_object_at_frame(object_id: int, frame: int):

    obj_id = str(object_id)

    seg = find_segment(obj_id, frame)

    if seg is None:
        raise HTTPException(
            status_code=404,
            detail="Object not present in this frame"
        )

    start_frame = seg["start_frame"]
    bbox_index = frame - start_frame

    bboxes = seg["bboxes"]

    if bbox_index < 0 or bbox_index >= len(bboxes):
        raise HTTPException(
            status_code=404,
            detail="Bounding box not available for this frame"
        )

    bbox = bboxes[bbox_index]

    return {
        "object_id": object_id,
        "frame": frame,
        "camera_id": seg["camera_id"],
        "bbox": bbox
    }
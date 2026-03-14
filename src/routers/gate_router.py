from fastapi import APIRouter, HTTPException
import cv2
import os
from config.settings import VIDEO_PATHS
from src.utils.json_utils import load_json

router = APIRouter()

vehicle_history = None
objects = None
fps = None


def init_router(history, data_objects, data_fps):
    global vehicle_history, objects, fps
    vehicle_history = history
    objects = data_objects
    fps = data_fps


@router.get("/gate_sequence")
def gate_sequence(object_id: int):

    sequence = []

    for event in vehicle_history:

        if event["object_id"] == object_id:

            sequence.append({
                "camera": event["camera"],
                "fence": event["fence"],
                "event": event["event"],
                "frame": event["frame"]
            })

    if not sequence:
        raise HTTPException(status_code=404, detail="No gate activity")

    sequence = sorted(sequence, key=lambda x: x["frame"])

    return {
        "object_id": object_id,
        "gate_sequence": sequence
    }


@router.get("/gate_clip")
def gate_clip(object_id: int, frame: int, camera: int):

    video_path = VIDEO_PATHS.get(camera)

    if not video_path:
        raise HTTPException(status_code=404, detail="Camera not found")

    obj_id = str(object_id)

    if obj_id not in objects:
        raise HTTPException(status_code=404, detail="Object not found")

    segments = objects[obj_id]["segments"]

    segment = None

    for seg in segments:

        if seg["camera_id"] == camera and seg["start_frame"] <= frame <= seg["end_frame"]:
            segment = seg
            break

    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")

    start = max(frame - 30, segment["start_frame"])
    end = min(frame + 30, segment["end_frame"])

    config_json = load_json("config/config_files.json")["app.py"]
    clip_output_dir = config_json.get("CLIP_OUTPUT_DIR", "clips")
    os.makedirs(clip_output_dir, exist_ok=True)

    out_path = f"{clip_output_dir}/gate_{object_id}_{frame}.mp4"

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = None

    current = start

    while current <= end:

        ret, frame_img = cap.read()

        if not ret:
            break

        idx = current - segment["start_frame"]

        if idx < len(segment["bboxes"]):

            x,y,w,h = segment["bboxes"][idx]

            cv2.rectangle(frame_img,(x,y),(x+w,y+h),(0,255,0),3)

        if abs(current - frame) <= 2:

            cv2.putText(
                frame_img,
                "GATE EVENT",
                (50,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0,0,255),
                3
            )

        if out is None:

            h,w = frame_img.shape[:2]

            out = cv2.VideoWriter(out_path, fourcc, fps, (w,h))

        out.write(frame_img)

        current += 1

    cap.release()

    if out:
        out.release()

    return {
        "clip_url": f"/{out_path}"
    }
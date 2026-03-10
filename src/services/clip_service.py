import cv2
import os
from config.settings import VIDEO_PATHS, CLIP_OUTPUT_DIR


def generate_object_clip(object_id, objects, fps):

    obj_id = str(object_id)

    if obj_id not in objects:
        return None

    segments = objects[obj_id]["segments"]

    os.makedirs(CLIP_OUTPUT_DIR, exist_ok=True)

    final_path = f"{CLIP_OUTPUT_DIR}/object_{object_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = None

    for seg in segments:

        cam = seg["camera_id"]
        video_path = VIDEO_PATHS[cam]

        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, seg["start_frame"])

        for bbox in seg["bboxes"]:

            ret, frame = cap.read()

            if not ret:
                break

            x,y,w,h = bbox

            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

            if out is None:

                h_frame, w_frame = frame.shape[:2]

                out = cv2.VideoWriter(
                    final_path,
                    fourcc,
                    fps,
                    (w_frame, h_frame)
                )

            out.write(frame)

        cap.release()

    if out:
        out.release()

    return final_path
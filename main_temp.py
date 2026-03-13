import cv2
import numpy as np
import json
from collections import defaultdict
from src.utils.json_utils import load_json


# -------------------------
# CONFIG
# -------------------------

config_json = load_json("config/config_files.json")["main.py"]
track_specific = True
VIDEO_PATHS = {
    i+1: x for i, x in enumerate(config_json["VIDEO_PATHS"])
}

GT_FILE = config_json["GT_FILE"]
TARGET_OBJECT = config_json["TARGET_OBJECT"]
OUTPUT_VIDEO = config_json["OUTPUT_VIDEO"]
OUTPUT_JSON = config_json["OUTPUT_JSON"]


# -------------------------
# Parse Ground Truth
# -------------------------

def parse_ground_truth(gt_file):

    data = defaultdict(list)

    with open(gt_file) as f:

        for line in f:

            cam, obj, frame, x, y, w, h, _, _ = map(float, line.split())

            cam = int(cam)
            obj = int(obj)
            frame = int(frame)

            # ONLY process target object
            if obj != TARGET_OBJECT and track_specific:
                continue

            data[(cam, frame)].append(
                (obj, int(x), int(y), int(w), int(h))
            )

    return data


# -------------------------
# Fence Structures
# -------------------------

entry_counts = defaultdict(int)
exit_counts = defaultdict(int)

fences = {i+1: [] for i in range(len(VIDEO_PATHS))}
drawing_points = []

object_current_fence = {}
transitions = []

vehicle_history = []
fence_usage = defaultdict(list)


# -------------------------
# Tracking Analytics (from code2)
# -------------------------

tracking_analytics = {
    "video_metadata": {
        "fps": None
    },
    "objects": defaultdict(lambda: {"segments": []})
}

active_segments = {}


# -------------------------
# Mouse Callback
# -------------------------

def mouse_callback(event, x, y, flags, param):

    global drawing_points

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing_points.append((x, y))


# -------------------------
# Assign Fence Type
# -------------------------

def assign_fence_type():

    while True:

        choice = input("\nAssign fence type (e=entry, x=exit): ").strip().lower()

        if choice == "e":
            return "entry"

        if choice == "x":
            return "exit"

        print("Invalid input.")


# -------------------------
# Fence Setup UI
# -------------------------

def setup_fences(frame, cam_id):

    global drawing_points

    win_name = f"Cam{cam_id} Fence Setup"

    cv2.namedWindow(win_name)
    cv2.setMouseCallback(win_name, mouse_callback)

    print(f"\nDraw fences for CAM{cam_id}")

    while True:

        temp = frame.copy()

        for p in drawing_points:
            cv2.circle(temp, p, 5, (0,0,255), -1)

        if len(drawing_points) > 1:
            cv2.polylines(temp,[np.array(drawing_points)],False,(0,255,0),2)

        for i,f in enumerate(fences[cam_id]):

            poly = f["polygon"]
            ftype = f["type"]

            color = (200,200,200)

            if ftype == "entry":
                color = (255,0,0)

            if ftype == "exit":
                color = (0,165,255)

            cv2.polylines(temp,[np.array(poly)],True,color,2)

            label = f"F{i}(?)" if ftype is None else f"F{i}({ftype[0].upper()})"

            x0,y0 = poly[0]

            cv2.putText(
                temp,
                label,
                (x0,y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        cv2.imshow(win_name,temp)

        key = cv2.waitKey(1)

        if key == ord("n"):

            if len(drawing_points) >= 3:

                fences[cam_id].append({
                    "polygon": drawing_points.copy(),
                    "type": None
                })

                drawing_points.clear()

        if key == ord("a"):

            if len(fences[cam_id]) > 0 and fences[cam_id][-1]["type"] is None:

                ftype = assign_fence_type()
                fences[cam_id][-1]["type"] = ftype

        if key == ord("r"):
            drawing_points.clear()

        if key == ord("s"):
            break

    cv2.destroyWindow(win_name)


# -------------------------
# Main Processing
# -------------------------

def main():

    data = parse_ground_truth(GT_FILE)

    # -------------------------
    # Open Cameras
    # -------------------------

    cameras = {}

    for cam_id, path in VIDEO_PATHS.items():
        cameras[cam_id] = cv2.VideoCapture(path)

    first_cam = cameras[1]

    fps = int(first_cam.get(cv2.CAP_PROP_FPS))
    width = int(first_cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(first_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    tracking_analytics["video_metadata"]["fps"] = fps

    max_frames = fps * 60

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video_out = cv2.VideoWriter(
        OUTPUT_VIDEO,
        fourcc,
        fps,
        (width * len(cameras), height)
    )

    # -------------------------
    # Fence Setup
    # -------------------------

    for cam_id, cap in cameras.items():

        ret, frame = cap.read()

        if ret:
            setup_fences(frame, cam_id)

        cap.set(cv2.CAP_PROP_POS_FRAMES,0)

    frame_id = 0

    # -------------------------
    # Tracking Loop
    # -------------------------

    while True:

        if frame_id >= max_frames:
            break

        frames = {}

        for cam_id, cap in cameras.items():

            ret, frame = cap.read()

            if not ret:
                return

            frames[cam_id] = frame

        for cam_id, frame in frames.items():

            # Draw fences

            for i,f in enumerate(fences[cam_id]):

                poly = f["polygon"]
                ftype = f["type"]

                color = (200,200,200)

                if ftype == "entry":
                    color = (255,0,0)

                if ftype == "exit":
                    color = (0,165,255)

                cv2.polylines(frame,[np.array(poly)],True,color,2)

            if (cam_id,frame_id) not in data:
                continue

            for obj,x,y,w,h in data[(cam_id,frame_id)]:
                if obj != TARGET_OBJECT and track_specific:
                    continue
                cx = int(x + w/2)
                cy = int(y + h)

                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                cv2.circle(frame,(cx,cy),4,(0,0,255),-1)

                # -------------------------
                # Tracking Segment Analytics
                # -------------------------

                key = (obj, cam_id)

                bbox = [x,y,w,h]

                if key not in active_segments:

                    active_segments[key] = {
                        "camera_id": cam_id,
                        "start_frame": frame_id,
                        "end_frame": frame_id,
                        "bboxes": [bbox]
                    }

                else:

                    seg = active_segments[key]

                    if frame_id == seg["end_frame"] + 1:

                        seg["end_frame"] = frame_id
                        seg["bboxes"].append(bbox)

                    else:

                        tracking_analytics["objects"][str(obj)]["segments"].append(dict(seg))

                        active_segments[key] = {
                            "camera_id": cam_id,
                            "start_frame": frame_id,
                            "end_frame": frame_id,
                            "bboxes": [bbox]
                        }

                # -------------------------
                # Fence Analytics
                # -------------------------

                current_fence = None
                current_type = None

                for i,f in enumerate(fences[cam_id]):

                    poly = f["polygon"]
                    ftype = f["type"]

                    inside = cv2.pointPolygonTest(np.array(poly),(cx,cy),False)

                    if inside >= 0:

                        current_fence = f"cam{cam_id}_fence_{i}"
                        current_type = ftype
                        break

                prev_fence = object_current_fence.get(obj)

                if prev_fence != current_fence:

                    if current_fence is not None:

                        if current_type == "entry":
                            entry_counts[current_fence] += 1
                            event = "entry"

                        elif current_type == "exit":
                            exit_counts[current_fence] += 1
                            event = "exit"

                        else:
                            event = "unknown"

                        event_record = {
                            "object_id": obj,
                            "camera": cam_id,
                            "fence": current_fence,
                            "event": event,
                            "frame": frame_id
                        }

                        vehicle_history.append(event_record)

                        fence_usage[current_fence].append(event_record)

                    if prev_fence and current_fence:

                        transitions.append({
                            "object_id": obj,
                            "from": prev_fence,
                            "to": current_fence,
                            "frame": frame_id
                        })

                    object_current_fence[obj] = current_fence

        combined = np.hstack([frames[i] for i in sorted(frames)])

        video_out.write(combined)

        cv2.imshow("Tracking + Digital Fences",combined)

        if cv2.waitKey(1) == 27:
            break

        frame_id += 1


    # -------------------------
    # Finalize Open Segments
    # -------------------------

    for (obj,_), seg in active_segments.items():

        tracking_analytics["objects"][str(obj)]["segments"].append(dict(seg))


    # -------------------------
    # Save Fence Analytics
    # -------------------------

    fence_analytics = {
        "entry_counts": dict(entry_counts),
        "exit_counts": dict(exit_counts),
        "fence_usage": fence_usage,
        "vehicle_history": vehicle_history,
        "transitions": transitions
    }

    with open(OUTPUT_JSON,"w") as f:
        json.dump(fence_analytics,f,indent=2)


    # -------------------------
    # Save Tracking Analytics
    # -------------------------

    # convert defaultdict → dict

    tracking_output = {
        "video_metadata": tracking_analytics["video_metadata"],
        "objects": dict(tracking_analytics["objects"])
    }

    with open("video_analytics.json","w") as f:
        json.dump(tracking_output,f,indent=2)


    # -------------------------
    # Cleanup
    # -------------------------

    for cap in cameras.values():
        cap.release()

    video_out.release()

    cv2.destroyAllWindows()


# -------------------------

if __name__ == "__main__":
    main()
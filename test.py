import cv2
import ollama
import os

VIDEO_PATH = "clips/gate_432_573.mp4"
QUESTION = "How many people are visible in this scene?"

FRAME_DIR = "tmp_frames"
os.makedirs(FRAME_DIR, exist_ok=True)


def extract_frames(video_path, seconds=5):

    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_to_extract = fps * seconds

    start = max(0, total_frames // 2 - frames_to_extract // 2)

    frame_paths = []

    for i in range(start, start + frames_to_extract, fps):  # 1 frame per second

        cap.set(cv2.CAP_PROP_POS_FRAMES, i)

        ret, frame = cap.read()

        if not ret:
            break

        path = f"{FRAME_DIR}/frame_{i}.jpg"

        cv2.imwrite(path, frame)

        frame_paths.append(path)

    cap.release()

    return frame_paths


def ask_moondream(question, image_path):

    response = ollama.chat(
        model="moondream:latest",
        messages=[
            {
                "role": "user",
                "content": question,
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]


def analyze_video():

    frames = extract_frames(VIDEO_PATH)

    print("Extracted frames:", frames)

    answers = []

    for img in frames:

        ans = ask_moondream(QUESTION, img)

        print(f"\nFrame {img} → {ans}")

        answers.append(ans)

    return answers


if __name__ == "__main__":

    results = analyze_video()

    print("\nFinal collected answers:\n")

    for r in results:
        print("-", r)
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

VIDEO_PATHS = {
    1: os.getenv("VIDEO_CAM1"),
    2: os.getenv("VIDEO_CAM2")
}

TRACKING_METADATA = os.getenv("TRACKING_METADATA")
FENCE_METADATA = os.getenv("FENCE_METADATA")

CLIP_OUTPUT_DIR = os.getenv("CLIP_OUTPUT_DIR")
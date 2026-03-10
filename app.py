from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.utils.json_utils import load_json
from config.settings import TRACKING_METADATA, FENCE_METADATA

from src.routers import (
    object_router,
    fence_router,
    clip_router,
    gate_router,
    chat_router
)

app = FastAPI(title="Video Analytics Query API")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/clips", StaticFiles(directory="clips"), name="clips")

templates = Jinja2Templates(directory="templates")

tracking_data = load_json(TRACKING_METADATA)
fence_data = load_json(FENCE_METADATA)

objects = tracking_data["objects"]
fps = tracking_data["video_metadata"]["fps"]

fence_usage = fence_data["fence_usage"]
vehicle_history = fence_data["vehicle_history"]

object_router.init_router(objects, fps)
fence_router.init_router(fence_usage)
clip_router.init_router(objects, fps)
gate_router.init_router(vehicle_history, objects, fps)

app.include_router(object_router.router)
app.include_router(fence_router.router)
app.include_router(clip_router.router)
app.include_router(gate_router.router)
app.include_router(chat_router.router)
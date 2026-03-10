from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.utils.json_utils import load_json
config_json = load_json("config/config_files.json")["app.py"]
TRACKING_METADATA = config_json["TRACKING_METADATA"]
FENCE_METADATA = config_json["FENCE_METADATA"]

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
# chat_router.init_router commented out - tool executor not yet implemented
# chat_router.init_router(tool_executor)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(object_router.router)
app.include_router(fence_router.router)
app.include_router(clip_router.router)
app.include_router(gate_router.router)
app.include_router(chat_router.router)
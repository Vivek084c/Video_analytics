from fastapi import APIRouter, HTTPException

router = APIRouter()

fence_usage_data = None


def init_router(data):
    global fence_usage_data
    fence_usage_data = data


@router.get("/fence_usage")
def fence_usage(fence_id: str):

    if fence_id not in fence_usage_data:
        raise HTTPException(status_code=404, detail="Fence not found")

    return {
        "fence": fence_id,
        "usage": fence_usage_data[fence_id]
    }


@router.get("/fences")
def list_fences():

    return {
        "fences": list(fence_usage_data.keys())
    }
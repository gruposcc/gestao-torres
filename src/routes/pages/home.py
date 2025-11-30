from fastapi import APIRouter

router = APIRouter()


@router.get("/home")
async def home():
    return {"message": "Hello World"}

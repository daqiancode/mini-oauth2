from fastapi import APIRouter, Response
from app.config import env

router = APIRouter(tags=["Public"])


if env.WECHAT_MP_FILE and env.WECHAT_MP_FILE_CONTENT:
    @router.get(f"/{env.WECHAT_MP_FILE}")
    async def mp():
        return Response(content=env.WECHAT_MP_FILE_CONTENT, media_type="text/plain")

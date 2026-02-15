from fastapi import APIRouter, Depends
import json
from redis.asyncio import Redis
from starlette.websockets import WebSocket

from app.models.user import UserORM
from app.core.dependencies import get_current_user
from app.core.dependencies import get_redis
from app.core.websocket_manager import manager
notification_router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@notification_router.get('/')
async def get_notifications(
        user: UserORM = Depends(get_current_user),
        redis: Redis = Depends(get_redis)
):
    redis_key = f'notifications:user:{user.id}'
    raw_notifications = await redis.lrange(redis_key, 0, -1)
    notifications = [json.loads(n) for n in raw_notifications]

    return {
        "count": len(notifications),
        "notifications": notifications
    }

@notification_router.delete("/")
async def clear_notifications(
    user: UserORM = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    await redis.delete(f"notifications:user:{user.id}")
    return {"status": "cleared"}

@notification_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    print(f"!!! Пытаемся подключить юзера: {user_id}")
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(user_id)
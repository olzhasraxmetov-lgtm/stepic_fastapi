from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from app.core.dependencies import get_current_user
from app.core.dependencies import get_notification_service
from app.core.websocket_manager import manager
from app.models.user import UserORM
from app.services.notification import NotificationService

notification_router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@notification_router.get('/', summary='Получить список уведомлений',
                         description=(
                                 "### Типы уведомлений:\n\n"
                                 "1. **Лайк на комментарий**: Когда другой пользователь поставил лайк на ваш комментарий.\n"
                                 "2. **Ответ на комментарий**: Когда кто-то ответил на ваше сообщение."
                         ))

async def get_notifications(
        user: UserORM = Depends(get_current_user),
        notification_service: NotificationService = Depends(get_notification_service)
):
    notifications, unread_count= await notification_service.get_data(user.id)
    return {
        "total_count": len(notifications),
        "unread_count": int(unread_count),
        "notifications": notifications
    }

@notification_router.delete("/", summary='Удалить уведомления')
async def clear_notifications(
    user: UserORM = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.clear(user.id)
    return {"status": "cleared"}

@notification_router.patch("/{notification_id}read", summary='Удалить уведомление по id',
                           description='Удаляет уведомление в redis по id')
async def clear_notifications_by_notification_id(
    notification_id: str,
    user: UserORM = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.mark_as_read_by_id(user_id=user.id, notification_id=notification_id)

@notification_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(user_id)
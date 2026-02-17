import json
from datetime import datetime
import uuid
from redis.asyncio.client import Redis
from app.core.exceptions import NotFoundException


class NotificationService:
    def __init__(self, redis: Redis, ws_manager):
        self.redis = redis
        self.manager = ws_manager


    async def send_notification(self, target_user_id: int, payload: dict, key_prefix : str = 'notifications'):
        payload['id'] = str(uuid.uuid4())
        if 'created_at' not in payload:
            payload["created_at"] = datetime.now().isoformat()

        redis_key = f'{key_prefix}:user:{target_user_id}'
        unread_key = f'{key_prefix}:unread_count:{target_user_id}'

        await self.redis.lpush(redis_key, json.dumps(payload))
        await self.redis.ltrim(redis_key, 0, 19)
        await self.redis.expire(redis_key, 60 * 60 * 24 * 30)

        new_unread_count = await self.redis.incr(unread_key)

        ws_data = payload.copy()
        ws_data["unread_count"] = new_unread_count
        await self.manager.send_personal_message(ws_data, target_user_id)

    async def clear(self, user_id: int, key_prefix: str = 'notifications'):
        await self.redis.delete(f'{key_prefix}:user:{user_id}')
        await self.redis.delete(f'{key_prefix}:unread_count:{user_id}')

    async def get_data(self, user_id:int, key_prefix : str = 'notifications'):
        notif_key = f'{key_prefix}:user:{user_id}'
        unread_key = f'{key_prefix}:unread_count:{user_id}'
        raw_notifications = await self.redis.lrange(notif_key, 0, -1)
        notifications = [json.loads(n) for n in raw_notifications]
        unread_count = await self.redis.get(unread_key) or 0
        return notifications, unread_count

    async def mark_as_read_by_id(self, user_id: int, notification_id: str, key_prefix : str = 'notifications'):
        redis_key = f'{key_prefix}:user:{user_id}'
        unread_key = f'{key_prefix}:unread_count:{user_id}'

        raw_notifications = await self.redis.lrange(redis_key, 0, -1)

        for index, raw_item in enumerate(raw_notifications):
            item = json.loads(raw_item)
            if item.get('id') == notification_id:
                if not item.get('is_read'):
                    item['is_read'] = True

                    await self.redis.lset(redis_key, index, json.dumps(item))

                    current_unread = await self.redis.get(unread_key)
                    if current_unread and int(current_unread) > 0:
                        await self.redis.decr(unread_key)
                return item
        raise NotFoundException(message="Уведомление не найдено")
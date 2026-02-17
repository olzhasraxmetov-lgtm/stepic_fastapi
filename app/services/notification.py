import json
from datetime import datetime

from redis.asyncio.client import Redis


class NotificationService:
    def __init__(self, redis: Redis, ws_manager):
        self.redis = redis
        self.manager = ws_manager


    async def send_notification(self, target_user_id: int, payload: dict, key_prefix : str = 'notifications'):
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

    async def get_data(self, user_id:int,  key_prefix : str = 'notifications'):
        notif_key = f'{key_prefix}:user:{user_id}'
        unread_key = f'{key_prefix}:unread_count:{user_id}'
        raw_notifications = await self.redis.lrange(notif_key, 0, -1)
        notifications = [json.loads(n) for n in raw_notifications]
        unread_count = await self.redis.get(unread_key) or 0
        await self.redis.delete(unread_key)
        return notifications, unread_count
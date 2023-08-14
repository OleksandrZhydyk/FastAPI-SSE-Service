import asyncio
import json

from typing import Callable
from redis import asyncio as aioredis
from redis.asyncio.client import Redis

from src.config import Config


async def redis_client():
    return await aioredis.from_url(
        f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}",
        encoding="utf8", decode_responses=True
    )


async def listen_to_channel(filter_func: Callable, user_id: str, redis: Redis):
    listener = redis.pubsub()
    await listener.subscribe(Config.PUSH_NOTIFICATIONS_CHANNEL)
    while True:
        message = await listener.get_message()
        if message and message.get("type") == "message":
            message = json.loads(message["data"])
            if filter_func(user_id, message):
                yield {"data": message}
                await asyncio.sleep(0.1)
            await asyncio.sleep(1)
        else:
            print("There is no message.")
            await asyncio.sleep(1)

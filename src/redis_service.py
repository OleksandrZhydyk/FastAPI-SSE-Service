import json
import redis

from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from typing import Callable

from src.config import Config


async def redis_client():
    try:
        return await aioredis.from_url(
            f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}",
            encoding="utf8", decode_responses=True
        )
    except redis.exceptions.ConnectionError as e:
        print("Connection error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


async def listen_to_channel(filter_func: Callable, user_id: str, redis_conn: Redis):
    async with redis_conn.pubsub() as listener:
        await listener.subscribe(Config.PUSH_NOTIFICATIONS_CHANNEL)
        while True:
            message = await listener.get_message()
            if message is None:
                continue
            if message.get("type") == "message":
                message = json.loads(message["data"])
                if filter_func(user_id, message):
                    print(message)
                    yield {"data": message}
                    continue
            if message.get("type") == "error":
                print(message)
                break

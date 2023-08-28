from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock

from src.redis_service import redis_client, listen_to_channel
from src.utils import is_user_recipient


class AsyncContextManager:

    def __init__(self, listener):
        self.listener = listener

    async def __aenter__(self):
        return self.listener

    async def __aexit__(self, exc_type, exc, tb):
        pass


class RedisStub:

    def __init__(self, message):
        self.message = message

    def pubsub(self):
        return AsyncContextManager(self.Listener(self.message))

    class Listener:

        def __init__(self, message):
            self.message = message

        async def subscribe(self, channel_name):
            pass

        async def get_message(self):
            return self.message


CORRECT_MESSAGE_MOCK = {
    "type": "message",
    "data": '{"recipient_id": "user_id"}'
}


class TestRedisService(IsolatedAsyncioTestCase):

    @patch("src.redis_service.aioredis.from_url")
    async def test_connect_redis(self, redis_mock):
        async_mock = AsyncMock()
        redis_mock.return_value = async_mock()

        await redis_client()
        redis_mock.assert_called_with(
            "redis://REDIS_HOST:REDIS_PORT", encoding="utf8", decode_responses=True
        )

    async def test_listen_to_channel(self):
        generator = listen_to_channel(
            is_user_recipient, "user_id", RedisStub(CORRECT_MESSAGE_MOCK)
        )

        message = await generator.__anext__()
        self.assertEqual(message, {"data": {"recipient_id": "user_id"}})

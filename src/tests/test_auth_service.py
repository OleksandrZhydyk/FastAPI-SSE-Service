from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock

from starlette import status

from src.auth_service import get_headers_token, is_user_authenticated
from src.exceptions import HeadersValidationError, AuthenticationError


class MockResponse:

    def __init__(self, status_code, content, response_ok=True):
        self.status_code = status_code
        self.content = content
        self.ok = response_ok

    async def json(self):
        return self.content


class TestGetHeaders(TestCase):

    def test_get_headers_token(self):
        mock_headers = {"Authorization": "Bearer ACCESS_TOKEN"}
        token = get_headers_token(mock_headers)

        self.assertEqual(token, "Bearer ACCESS_TOKEN")

    def test_error_get_headers_token_no_token(self):
        mock_headers = {}
        with self.assertRaises(HeadersValidationError) as cm:
            get_headers_token(mock_headers)
        self.assertEqual("Credentials are not provided.", str(cm.exception.msg))

    def test_error_get_headers_token_incorrect_token_type(self):
        mock_headers = {"Authorization": "ACCESS_TOKEN"}
        with self.assertRaises(HeadersValidationError) as cm:
            get_headers_token(mock_headers)
        self.assertEqual("Incorrect token type.", str(cm.exception.msg))


class TestIsUserAuth(IsolatedAsyncioTestCase):

    @patch("src.auth_service.aiohttp.ClientSession")
    async def test_is_user_authenticated(self, mock_session):

        session_obj = mock_session.return_value
        async_mock = AsyncMock()
        async_mock.get.return_value = MockResponse(status_code=200, content={"user_id": "user_uuid"})
        session_obj.__aenter__.return_value = async_mock

        user = await is_user_authenticated("Bearer ACCESS_TOKEN")

        self.assertEqual(user, "user_uuid")
        session_obj.__aenter__.assert_awaited_once()
        async_mock.get.assert_called_with(
            "http://MAIN_HOST/api/v1/notifications/is_user_auth/",
            headers={
                "Authorization": "Bearer ACCESS_TOKEN",
            }
        )

    @patch("src.auth_service.aiohttp.ClientSession")
    async def test_error_is_user_authenticated_res_not_ok(self, mock_session):
        session_obj = mock_session.return_value
        async_mock = AsyncMock()
        async_mock.get.return_value = MockResponse(
            status_code=400, content={"error": "invalid_token"}, response_ok=False)
        session_obj.__aenter__.return_value = async_mock

        with self.assertRaises(AuthenticationError) as cm:
            await is_user_authenticated("Bearer ACCESS_TOKEN")

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, cm.exception.status)
        self.assertEqual({"error": "invalid_token"}, cm.exception.msg)
        async_mock.get.assert_awaited_once()
        session_obj.__aenter__.assert_awaited_once()

    @patch("src.auth_service.aiohttp.ClientSession")
    async def test_error_is_user_authenticated_no_user_id(self, mock_session):
        session_obj = mock_session.return_value
        async_mock = AsyncMock()
        async_mock.get.return_value = MockResponse(
            status_code=200, content="no_key_user_id")
        session_obj.__aenter__.return_value = async_mock

        with self.assertRaises(AuthenticationError) as cm:
            await is_user_authenticated("Bearer ACCESS_TOKEN")

        self.assertEqual("Incorrect data was provided by authentication server.", str(cm.exception.msg))
        self.assertEqual(status.HTTP_422_UNPROCESSABLE_ENTITY, cm.exception.status)
        async_mock.get.assert_awaited_once()
        session_obj.__aenter__.assert_awaited_once()

    async def test_error_is_user_authenticated_connection_failed(self):
        with self.assertRaises(AuthenticationError) as cm:
            await is_user_authenticated("Bearer ACCESS_TOKEN")
        self.assertEqual("Authentication API connection error.", str(cm.exception.msg))
        self.assertEqual(status.HTTP_504_GATEWAY_TIMEOUT, cm.exception.status)


import aiohttp
from starlette import status
from starlette.datastructures import Headers

from src.config import Config
from src.exceptions import HeadersValidationError, AuthenticationError


def get_headers_token(headers: Headers) -> str | None:
    authorization_header = headers.get("Authorization")
    if authorization_header is None:
        authorization_header = headers.get("authorization")
    if authorization_header is None:
        raise HeadersValidationError(msg="Credentials are not provided.", status=status.HTTP_403_FORBIDDEN)
    if authorization_header.startswith("Bearer "):
        return authorization_header
    raise HeadersValidationError(msg="Incorrect token type.", status=status.HTTP_403_FORBIDDEN)


async def is_user_authenticated(token: str) -> str | None:
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(
                    f"{Config.MAIN_HOST}/api/v1/notifications/is_user_auth/",
                    headers={"Authorization": token}
            )
        except aiohttp.ClientError:
            raise AuthenticationError(msg="Authentication API connection error.", status=status.HTTP_504_GATEWAY_TIMEOUT)
        if response.ok:
            res = await response.json()
            if isinstance(res, dict) and "user_id" in res:
                return res.get("user_id")
            raise AuthenticationError(
                msg="Incorrect data was provided by authentication server.",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        res = await response.json()
        raise AuthenticationError(msg=res, status=status.HTTP_401_UNAUTHORIZED)

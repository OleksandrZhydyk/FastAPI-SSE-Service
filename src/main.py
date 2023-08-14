import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from redis.asyncio.client import Redis
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from src.auth_service import get_headers_token, is_user_authenticated
from src.exceptions import create_response_for_exception, HeadersValidationError, AuthenticationError
from src.redis_service import listen_to_channel, redis_client
from src.utils import is_user_recipient

app = FastAPI(title="notification_service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return "OK"


# SSE implementation
@app.get("/notify")
async def notification(request: Request, redis: Redis = Depends(redis_client)):
    try:
        authorization_header = get_headers_token(request.headers)
    except HeadersValidationError as e:
        return create_response_for_exception(msg=e.msg, status=e.status)
    try:
        user_id = await is_user_authenticated(authorization_header)
        return EventSourceResponse(listen_to_channel(is_user_recipient, user_id, redis))
    except AuthenticationError as e:
        return create_response_for_exception(msg=e.msg, status=e.status)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

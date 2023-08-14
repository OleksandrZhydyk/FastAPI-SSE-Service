import json

from starlette.responses import Response


def create_response_for_exception(msg, status):
    return Response(content=json.dumps({"error": msg}), status_code=status)


class HeadersValidationError(Exception):
    def __init__(self, msg, status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg
        self.status = status


class AuthenticationError(Exception):
    def __init__(self, msg, status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg
        self.status = status

import os


class Config:
    if os.environ.get("TESTING"):
        MAIN_HOST = "http://MAIN_HOST"
        REDIS_HOST = "REDIS_HOST"
        REDIS_PORT = "REDIS_PORT"
        PUSH_NOTIFICATIONS_CHANNEL = "PUSH_NOTIFICATIONS_CHANNEL"
    else:
        MAIN_HOST = os.getenv("MAIN_HOST", "http://192.168.3.32:8000")
        REDIS_HOST = os.getenv("REDIS_HOST", "192.168.3.61")
        REDIS_PORT = os.getenv("REDIS_PORT", 6830)
        PUSH_NOTIFICATIONS_CHANNEL = os.getenv("PUSH_NOTIFICATIONS_CHANNEL", "notifications")

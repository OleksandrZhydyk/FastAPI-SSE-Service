### Server Side Event FastAPI Service

Simple FastAPI service that implements push notification 
feature on the backend. 

User authentication occurs by sending requests to an authentication server. The service captures events from a source using Redis pub/sub functionality and then forwards these events to recipients based on the `recipient_id` information contained within the event.

- Example of env file
```shell
MAIN_HOST=YOUR_AUTH_HOST
REDIS_HOST=YOUR_REDIS_HOST
REDIS_PORT=YOUR_REDIS_PORT
PUSH_NOTIFICATIONS_CHANNEL=YOUR_NAME_OF_NOTIFICATIONS_CHANNEL
```

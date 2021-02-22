import abc
from uuid import uuid4

import redis

SESSION_EXPIRATION_SECONDS = 120


class SessionManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def set_session(self, user_id: int) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def validate_user_session(self, user_id: int, session_key: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_session(self, user_id: int):
        raise NotImplementedError


class RedisSessionManager(SessionManager):
    redis: redis.Redis

    def __init__(self, redis_host, redis_port):
        self.redis = redis.Redis(host=redis_host, port=redis_port)

    def set_session(self, user_id: int) -> str:
        session_key = str(uuid4())
        self.redis.set(str(user_id), session_key, ex=SESSION_EXPIRATION_SECONDS)
        return session_key

    def validate_user_session(self, user_id: int, session_key: str) -> bool:
        return session_key == self.redis.get(str(user_id))

    def extend_session(self, user_id: int) -> bool:
        self.redis.expire(str(user_id), SESSION_EXPIRATION_SECONDS)
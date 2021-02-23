import abc
import os
from typing import Optional, Type
from uuid import uuid4

from redis.client import Redis

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
    redis: Redis

    def __init__(
            self,
            redis_host: Optional[str] = None,
            redis_port: Optional[int] = None,
            session_exp_seconds: int =SESSION_EXPIRATION_SECONDS,
            redis_cls: Type[Redis] = Redis
    ):
        if redis_host is None:
            redis_host = os.getenv('REDIS_HOST')

        if redis_port is not None:
            self.redis = redis_cls(host=redis_host, port=redis_port)
        else:
            self.redis = redis_cls(host=redis_host)

        self.session_exp_seconds = session_exp_seconds

    def set_session(self, user_id: int) -> str:
        session_key = str(uuid4())
        self.redis.set(str(user_id), session_key, ex=self.session_exp_seconds)
        return session_key

    def validate_user_session(self, user_id: int, session_key: str) -> bool:
        saved_key = self.redis.get(str(user_id))
        if saved_key:
            return session_key == saved_key.decode()

        return False

    def extend_session(self, user_id: int) -> bool:
        self.redis.expire(str(user_id), SESSION_EXPIRATION_SECONDS)
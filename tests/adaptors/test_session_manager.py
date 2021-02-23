from time import sleep

import fakeredis

from account.adaptors.session_manager import RedisSessionManager


def test_session():
    session_manager = RedisSessionManager(redis_cls=fakeredis.FakeStrictRedis)
    user_id = 323232
    session_key = session_manager.set_session(user_id)

    assert session_manager.validate_user_session(user_id, session_key)


def test_wrong_session_key():
    session_manager = RedisSessionManager(redis_cls=fakeredis.FakeStrictRedis)
    user_id = 323232

    session_key = session_manager.set_session(user_id)
    assert not session_manager.validate_user_session(user_id, session_key + 'a')


def test_session_expiration():
    session_manager = RedisSessionManager(redis_cls=fakeredis.FakeStrictRedis, session_exp_seconds=1)
    user_id = 323232
    session_key = session_manager.set_session(user_id)

    sleep(1)
    assert not session_manager.validate_user_session(user_id, session_key)

import pytest

from uuid import uuid4
from account.entity import Card
from account.service import handler, service_exceptions
from tests.conftest import FakeUnitOfWork, FakeSessionmanager


def setup_session_test():
    pin = '1838'
    salt = uuid4().hex
    pin_hash = Card.hash_pin(pin, salt)
    valid_card = Card(card_num=232, user_id=17, pin_salt_hash=salt + pin_hash)
    uow = FakeUnitOfWork(cards=[valid_card], accounts=[])
    session_manager = FakeSessionmanager()
    return valid_card, pin, uow, session_manager


def test_session():
    valid_card, pin, uow, session_manager = setup_session_test()

    session_key = handler.set_session(card_num=valid_card.card_num, pin=pin, uow=uow, session_manager=session_manager)
    assert session_key is not None


def test_incorrect_card_pin():
    valid_card, pin, uow, session_manager = setup_session_test()
    incorrect_pin = '2323'

    with pytest.raises(service_exceptions.IncorrectPin):
        handler.set_session(card_num=valid_card.card_num, pin=incorrect_pin, uow=uow, session_manager=session_manager)


def test_invalid_card():
    valid_card, pin, uow, session_manager = setup_session_test()

    with pytest.raises(service_exceptions.InvalidCardNum):
        handler.set_session(card_num=valid_card.card_num + 1, pin=pin, uow=uow, session_manager=session_manager)

from datetime import datetime

import pytest

from account.entity import Account, Card, AccountRecord
from account.service import handler, service_exceptions
from account.domain_exception import NegativeAccountBalanceException
from tests.conftest import FakeUnitOfWork, FakeSessionmanager


def setup_account_test(balance):
    card_num = 1323
    user_id = 17718
    session_manager = FakeSessionmanager()
    session_key = session_manager.set_session(user_id=user_id)

    account = Account(
        user_id=user_id,
        account_id=1, name='Test account',
        histories=[AccountRecord(balance=balance, action=AccountRecord.DEPOSIT, time_at=datetime.utcnow())]
    )

    uow = FakeUnitOfWork(
        cards=[Card(card_num=card_num, user_id=user_id, pin_salt_hash='something')],
        accounts=[account]
    )
    return card_num, account.account_id, session_key, uow, session_manager


@pytest.mark.parametrize('amount,balance', [(333, 23223), (3581, 0), (38467, 38467)])
def test_deposit(amount, balance):
    card_num, account_id, session_key, uow, session_manager = setup_account_test(balance)
    handler.account_action(
        session_key=session_key,
        account_id=account_id,
        action=AccountRecord.DEPOSIT,
        card_num=card_num,
        uow=uow,
        amount=amount,
        session_manager=session_manager
    )


@pytest.mark.parametrize('amount,balance', [(333, 23223), (9, 10), (38467, 38467), (1, 1)])
def test_withdrawal(amount, balance):
    card_num, account_id, session_key, uow, session_manager = setup_account_test(balance)
    handler.account_action(
        session_key=session_key,
        account_id=account_id,
        action=AccountRecord.WITHDRAWAL,
        card_num=card_num,
        uow=uow,
        amount=amount,
        session_manager=session_manager
    )


@pytest.mark.parametrize('amount,balance', [(2, 1), (1, 0), (100, 99), (124, 71)])
def test_invalid_withdrawal(amount, balance):
    balance = 3289
    card_num, account_id, session_key, uow, session_manager = setup_account_test(balance)
    with pytest.raises(NegativeAccountBalanceException):
        handler.account_action(
            session_key=session_key,
            account_id=account_id,
            action=AccountRecord.WITHDRAWAL,
            card_num=card_num,
            uow=uow,
            amount=balance + 1,
            session_manager=session_manager
        )


def test_invalid_session():
    card_num, account_id, session_key, uow, session_manager = setup_account_test(0)
    with pytest.raises(service_exceptions.InvalidSesionKey):
        handler.account_action(
            session_key=session_key + 'a',
            account_id=account_id,
            action=AccountRecord.DEPOSIT,
            card_num=card_num,
            uow=uow,
            amount=10,
            session_manager=session_manager
        )


def test_invalid_card():
    card_num, account_id, session_key, uow, session_manager = setup_account_test(0)
    with pytest.raises(service_exceptions.InvalidCardNum):
        handler.account_action(
            session_key=session_key,
            account_id=account_id,
            action=AccountRecord.DEPOSIT,
            card_num=card_num + 1,
            uow=uow,
            amount=10,
            session_manager=session_manager
        )
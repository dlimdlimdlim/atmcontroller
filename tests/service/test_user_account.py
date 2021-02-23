import pytest

from account.entity import Account, Card
from account.service import handler, service_exceptions
from tests.conftest import FakeUnitOfWork, FakeSessionmanager


@pytest.fixture
def setup_account_test():
    card_num = 1373
    user_id = 1771
    session_manager = FakeSessionmanager()
    session_key = session_manager.set_session(user_id=user_id)

    accounts = [
        Account(user_id=user_id, account_id=1, name='Test account', histories=[]),
        Account(user_id=user_id, account_id=2, name='Test account', histories=[]),
        Account(user_id=333, account_id=3, name='Test account', histories=[]),
        Account(user_id=444, account_id=3, name='Test account', histories=[]),
    ]
    user_accounts = {account.account_id: account for account in accounts if account.user_id == user_id}
    uow = FakeUnitOfWork(
        cards=[Card(card_num=card_num, user_id=user_id, pin_salt_hash='something')],
        accounts=accounts
    )
    yield card_num, user_id, session_key, user_accounts, uow, session_manager


def test_get_user_accounts(setup_account_test):
    card_num, expected_user_id, session_key, expected_user_accounts, uow, session_manager = setup_account_test
    accounts = handler.get_accounts(
        session_key=session_key,
        card_num=card_num,
        uow=uow,
        session_manager=session_manager
    )

    assert len(accounts) == len(expected_user_accounts)
    for account in accounts:
        assert account.user_id == expected_user_id
        assert expected_user_accounts[account.account_id].name == account.name


def test_invalid_session(setup_account_test):
    card_num, expected_user_id, session_key, expected_user_accounts, uow, session_manager = setup_account_test
    with pytest.raises(service_exceptions.InvalidSesionKey):
        handler.get_accounts(
            session_key=session_key + '3',
            card_num=card_num,
            uow=uow,
            session_manager=session_manager
        )


def test_invalid_card(setup_account_test):
    card_num, expected_user_id, session_key, expected_user_accounts, uow, session_manager = setup_account_test
    with pytest.raises(service_exceptions.InvalidCardNum):
        handler.get_accounts(
            session_key=session_key,
            card_num=card_num + 1,
            uow=uow,
            session_manager=session_manager
        )

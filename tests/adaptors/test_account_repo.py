from datetime import datetime

import pytest

from account.adaptors.account_repo import DjangoAccountRepo
from account.entity import Account
from account.value_objects import AccountRecord
from account.service.service_exceptions import AccountHistoryIntegrityError
from atmdjango.atm_app.models import AccountHistory, BankAccount, BankCard


@pytest.fixture
def setup_cards():
    cards = {
        32323: dict(user_id=38282, pin_hash='Iam-king-of-the-world!'),
        17: dict(user_id=38282, pin_hash='Showmethemoney'),
        222234: dict(user_id=97666, pin_hash='yayayayayaya')
    }

    for card_num, card_info in cards.items():
        BankCard.objects.create(card_number=card_num, user_id=card_info['user_id'], pin_hash=card_info['pin_hash'])

    yield cards


@pytest.mark.django_db
def test_get_card(setup_cards):
    repo = DjangoAccountRepo()
    for card_num, card_info in setup_cards.items():
        card = repo.get_card(card_num)

        assert card.card_num == card_num
        assert card.user_id == card_info['user_id']
        assert card.pin_salt_hash == card_info['pin_hash']


@pytest.mark.django_db
def test_non_existing_card(setup_cards):
    repo = DjangoAccountRepo()

    card_num = max(setup_cards) + 1
    card = repo.get_card(card_num)
    assert card is None


@pytest.fixture
def setup_accounts():
    user_account_names = {
        379: ['Mudamuda!', 'you are already dead', 'Dora'],
        101: ['Gandalf', 'another one bites the dust']
    }
    user_account_ids = {
        379: set(),
        101: set()
    }
    account_names = dict()
    for user_id, account_name_list in user_account_names.items():
        for name in account_name_list:
            account = BankAccount.objects.create(user_id=user_id, account_name=name)
            user_account_ids[user_id].add(account.id)
            account_names[account.id] = name

    yield user_account_ids, account_names


@pytest.mark.django_db
def test_get_user_accounts(setup_accounts):
    user_account_ids, account_names = setup_accounts
    repo = DjangoAccountRepo()

    for user_id, account_ids in user_account_ids.items():
        accounts = repo.get_user_accounts(user_id)

        assert len(accounts) == len(account_ids)
        for account in accounts:
            assert account.account_id in account_ids
            assert account_names[account.account_id] == account.name


@pytest.mark.django_db
def test_get_non_existing_user_accounts(setup_accounts):
    user_account_ids, _ = setup_accounts
    repo = DjangoAccountRepo()

    user_id = max(user_account_ids.keys()) + 1
    accounts = repo.get_user_accounts(user_id)
    assert len(accounts) == 0


@pytest.fixture
def account_with_history():
    user_id = 185
    account_name = 'bankrupt'
    last_record_index = 38271
    balance = 37273
    last_operation = AccountRecord.DEPOSIT
    account = BankAccount.objects.create(user_id=user_id, account_name=account_name)

    AccountHistory.objects.create(
        account_id=account.id,
        operation=AccountRecord.DEPOSIT,
        account_balance=balance,
        operation_index=last_record_index
    )

    yield user_id, account.id, last_record_index, account_name, balance, last_operation


@pytest.mark.django_db
def test_get_user_account(account_with_history):
    user_id, account_id, last_record_index, account_name, balance, last_operation = account_with_history
    repo = DjangoAccountRepo()

    account = repo.get_user_account(user_id=user_id, account_id=account_id)

    assert account.account_id == account_id
    assert account.histories[-1].record_index == last_record_index
    assert account.histories[-1].action == last_operation
    assert account.name == account_name
    assert account.user_id == user_id
    assert account.get_balance() == balance


@pytest.mark.django_db
def test_get_user_accout_overwrite_last_record(account_with_history):
    user_id, account_id, last_record_index, account_name, balance, last_operation = account_with_history

    new_balance = 11
    AccountHistory.objects.create(
        account_id=account_id,
        operation=AccountRecord.WITHDRAWAL,
        account_balance=new_balance,
        operation_index=last_record_index + 1
    )

    repo = DjangoAccountRepo()

    account = repo.get_user_account(user_id=user_id, account_id=account_id)

    assert account.account_id == account_id
    assert account.histories[-1].record_index == last_record_index + 1
    assert account.histories[-1].action == AccountRecord.WITHDRAWAL
    assert account.name == account_name
    assert account.user_id == user_id
    assert account.get_balance() == new_balance


@pytest.mark.django_db
def test_update_account():
    account = Account(
        account_id=3232,
        user_id=822,
        name='France is Bacon',
        histories=[
            AccountRecord(action=AccountRecord.DEPOSIT, balance=376, record_index=39, time_at=datetime.utcnow())
        ]
    )

    new_histories = [
        AccountRecord(action=AccountRecord.DEPOSIT, balance=5000, record_index=40),
        AccountRecord(action=AccountRecord.WITHDRAWAL, balance=400, record_index=41)
    ]
    account.new_histories = new_histories
    repo = DjangoAccountRepo()

    repo.update_account(account)

    for record in new_histories:
        history_data = AccountHistory.objects.get(account_id=account.account_id, operation_index=record.record_index)
        assert history_data.operation == record.action
        assert history_data.account_balance == record.balance


@pytest.mark.django_db(transaction=True)
def test_update_account_integrity_failure():
    account = Account(
        account_id=3232,
        user_id=822,
        name='France is Bacon',
        histories=[
            AccountRecord(action=AccountRecord.DEPOSIT, balance=376, record_index=39, time_at=datetime.utcnow())
        ]
    )

    new_histories = [
        AccountRecord(action=AccountRecord.DEPOSIT, balance=5000, record_index=40),
        AccountRecord(action=AccountRecord.WITHDRAWAL, balance=400, record_index=41)
    ]
    account.new_histories = new_histories

    AccountHistory.objects.create(
        account_id=account.account_id,
        operation_index=40, account_balance=7899,
        operation=AccountRecord.WITHDRAWAL
    )

    repo = DjangoAccountRepo()

    with pytest.raises(AccountHistoryIntegrityError):
        repo.update_account(account)

    # check if no new history is created by repo
    assert len(AccountHistory.objects.all()) == 1

import pytest

from account.adaptors.account_repo import DjangoAccountRepo
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


@pytest.mark.django_db
def test_get_user_account():
    pass


@pytest.mark.django_db
def test_update_account():
    pass
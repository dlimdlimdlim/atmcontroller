import abc
from typing import List, Set, Optional

from django.db.models import ObjectDoesNotExist

from account.entity import Account, AccountRecord, Card
from atmdjango.atm_app.models import BankCard, BankAccount, AccountHistory


class AccountRepository(metaclass=abc.ABCMeta):

    def __init__(self):
        self.seen_accounts: Set[Account] = set()

    @abc.abstractmethod
    def get_card(self, card_num: int) -> Optional[Card]:
        raise NotImplementedError

    # this function is for read only, accounts retrieved from this function should not be modified
    @abc.abstractmethod
    def view_user_accounts(self, user_id: int) -> List[Account]:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_user_account(self, user_id) -> Optional[Account]:
        raise NotImplementedError

    def get_account(self, user_id: int) -> Optional[Account]:
        account = self._get_user_account(user_id)
        if account is None:
            return
        self.seen_accounts.add(account)
        return account

    @abc.abstractmethod
    def update_account(self, account_id: int, record: AccountRecord):
        raise NotImplementedError


class DjangoAccountRepo(AccountRepository):

    def get_card(self, card_num: int) -> Optional[Card]:
        try:
            card = BankCard.objects.get(card_number=card_num).to_domain()
        except ObjectDoesNotExist:
            return None

        return card

    def view_user_accounts(self, user_id: int) -> List[Account]:
        accounts = []
        for account_data in BankAccount.objects.filter(user_id=user_id):
            account_last_record = AccountRecord.objects.filter(account_id=account_data.id).last('created_at')
            histories = []
            if account_last_record:
                histories = [account_last_record.to_domain()]

            accounts.append(Account(user_id=user_id, account_id=account_data.id, histories=histories))

        return accounts

    def _get_user_account(self, user_id: int, account_id: int) -> Optional[Account]:
        try:
            account_data = BankAccount.objects.get(user_id=user_id, id=account_id)
        except ObjectDoesNotExist:
            return None

        histories = []
        account_last_record = AccountRecord.objects.filter(account_id=account_data.id).last('created_at')
        if account_last_record:
            histories = [account_last_record.to_domain()]

        return Account(user_id=user_id, account_id=account_data.id, histories=histories)

    def update_account(self, account_id: int, record: AccountRecord):
        AccountHistory.objects.create(account_id=account_id, account_balance=record.balance, operation=record.action)

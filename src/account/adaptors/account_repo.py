import abc
from uuid import uuid4
from typing import List, Set

import redis
from django.db.models import ObjectDoesNotExist

from account.entity import Account, AccountRecord, Card, User
from atmdjango.atm_app.models import BankCard, BankAccount, AccountHistory
from account.service import service_exceptions


class AccountRepository(metaclass=abc.ABCMeta):

    def __init__(self):
        self.seen_accounts: Set[Account] = set()

    @abc.abstractmethod
    def get_card(self, card_num: int) -> Card:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_by_card(self, card_num: int) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def view_user_accounts(self, user_id: int) -> List[Account]:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_user_account(self, user_id) -> Account:
        raise NotImplementedError

    def get_account(self, user_id: int) -> Account:
        account = self._get_user_account(user_id)
        self.seen_accounts.add(account)
        return account

    @abc.abstractmethod
    def update_account(self, record: AccountRecord):
        raise NotImplementedError


class DjangoAccountRepo(AccountRepository):

    def get_card(self, card_num: int) -> Card:
        try:
            card = BankCard.objects.get(card_number=card_num).to_entity()
        except ObjectDoesNotExist:
            raise service_exceptions.InvalidCardNum(f'card with number {card_num} does not exist!')

        return card

    def view_user_accounts(self, user_id: int) -> List[Account]:
        accounts = []
        for account_data in BankAccount.objects.filter(user_id=user_id):
            account_last_record = AccountRecord.objects.filter(account_id=account_data.id).last('created_at')
            histories = []
            if account_last_record:
                histories = [account_last_record.to_entity()]

            accounts.append(Account(user_id=user_id, account_id=account_data.id, histories=histories))

        return accounts

    def _get_user_account(self, user_id: int, account_id: int) -> Account:
        try:
            account_data = BankAccount.objects.get(user_id=user_id, id=account_id)
        except ObjectDoesNotExist:
            raise service_exceptions.InvalidAccount(f'account {account_id} for user {user_id} does not exist!')

        histories = []
        account_last_record = AccountRecord.objects.filter(account_id=account_data.id).last('created_at')
        if account_last_record:
            histories = [account_last_record.to_entity()]

        return Account(user_id=user_id, account_id=account_data.id, histories=histories)

    def update_account(self, record: AccountRecord):
        AccountHistory.create_from_entity(record)
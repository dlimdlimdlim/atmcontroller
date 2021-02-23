import abc
from typing import List, Set, Optional

from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist

from account.entity import Account, AccountRecord, Card
from account.service import service_exceptions
from atmdjango.atm_app.models import BankCard, BankAccount, AccountHistory


class AccountRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_card(self, card_num: int) -> Optional[Card]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_accounts(self, user_id: int) -> List[Account]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_account(self, user_id: int,  account_id: int) -> Optional[Account]:
        raise NotImplementedError

    @abc.abstractmethod
    def update_account(self, account: Account):
        raise NotImplementedError


class DjangoAccountRepo(AccountRepository):

    def get_card(self, card_num: int) -> Optional[Card]:
        try:
            card = BankCard.objects.get(card_number=card_num).to_domain()
        except ObjectDoesNotExist:
            return None

        return card

    def get_user_accounts(self, user_id: int) -> List[Account]:
        accounts = []
        for account_data in BankAccount.objects.filter(user_id=user_id):
            account_last_record = AccountHistory.objects.filter(
                account_id=account_data.id
            ).order_by('operation_index').last()
            histories = []
            if account_last_record:
                histories = [account_last_record.to_domain()]

            accounts.append(
                Account(
                    user_id=user_id,
                    name=account_data.account_name,
                    account_id=account_data.id,
                    histories=histories
                )
            )

        return accounts

    def get_user_account(self, user_id: int, account_id: int) -> Optional[Account]:
        try:
            account_data = BankAccount.objects.get(user_id=user_id, id=account_id)
        except ObjectDoesNotExist:
            return None

        histories = []
        account_last_record = AccountHistory.objects.filter(account_id=account_data.id).last('created_at')
        if account_last_record:
            histories = [account_last_record.to_domain()]

        return Account(user_id=user_id, account_id=account_data.id, histories=histories)

    def update_account(self, account: Account):
        for record in account.new_histories:
            try:
                AccountHistory.objects.create(
                    account_id=account.account_id,
                    operation_index=record.record_index,
                    account_balance=record.balance,
                    operation=record.action
                )
            except IntegrityError as error:
                raise service_exceptions.AccountHistoryIntegrityError(
                    f'Integrity error on account record update '
                    f'to account {account.account_id} with record index {record.record_index}'
                ) from error

import hashlib
from typing import List, Optional

from account.value_objects import AccountRecord
from account.domain_exception import InvalidAmount, NegativeAccountBalanceException


class Card:
    def __init__(self, card_num: int, user_id: int, pin_salt_hash: str):
        self.card_num = card_num
        self.user_id = user_id
        self.pin_salt_hash = pin_salt_hash

    def validate_pin(self, pin: str):
        salt = self.pin_salt_hash[:32]
        pin_hash = self.pin_salt_hash[32:]
        return pin_hash == self.hash_pin(pin, salt)

    @staticmethod
    def hash_pin(pin: str, salt: str):
        return hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex()


class Account:
    def __init__(self, account_id: int, user_id: int, name: str, histories: List[AccountRecord]):
        self.account_id = account_id
        self.user_id = user_id
        self.histories = histories
        self.histories.sort(key=lambda x: x.record_index)
        self.new_histories: List[AccountRecord] = []
        self.name = name
        self.last_record_index = 0

        if self.histories:
            self.last_record_index = self.histories[-1].record_index

    def get_balance(self) -> int:
        if not self.histories:
            return 0

        return self.histories[-1].balance

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmount('Withdrawal amount must be larger than zero')

        balance = self.get_balance() - amount
        if balance < 0:
            raise NegativeAccountBalanceException(f'Not enough account blance to withdraw {amount}')

        if self.new_histories:
            new_record_index = self.new_histories[-1].record_index + 1
        else:
            new_record_index = self.histories[-1].record_index + 1

        new_record = AccountRecord(
            action=AccountRecord.WITHDRAWAL,
            balance=balance,
            record_index=new_record_index,
            time_at=None
        )
        self.new_histories.append(new_record)

    def deposit(self, amount):
        if amount < 0:
            raise InvalidAmount('Deposit amount must be lareger than zero')

        balance = self.get_balance() + amount
        if self.new_histories:
            new_record_index = self.new_histories[-1].record_index + 1
        else:
            new_record_index = self.histories[-1].record_index + 1

        new_record = AccountRecord(
            action=AccountRecord.WITHDRAWAL,
            balance=balance,
            record_index=new_record_index,
            time_at=None
        )
        self.new_histories.append(new_record)

    def commit_new_histories(self):
        self.histories = self.histories + self.new_histories
        self.new_histories = []


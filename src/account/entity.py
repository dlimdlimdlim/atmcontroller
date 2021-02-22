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
    def __init__(self, account_id: int, user_id: int, histories: List[AccountRecord]):
        self.account_id = account_id
        self.user_id = user_id
        self.histories = histories
        self.histories.sort(key=lambda x: x.time_at)
        self.new_histories: List[AccountRecord] = []

    def get_balance(self) -> int:
        if not self.histories:
            return 0

        return self.histories[-1].balance

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmount('Withdrawal amount must be lareger than zero')

        balance = self.get_balance() - amount
        if balance < 0:
            raise NegativeAccountBalanceException(f'Not enough account blance to withdraw {amount}')

        new_record = AccountRecord(action=AccountRecord.WITHDRAWL, balance=balance, time_at=None)
        self.histories.append(new_record)
        self.new_histories.append(new_record)

    def deposit(self, amount):
        if amount < 0:
            raise InvalidAmount('Deposit amount must be lareger than zero')

        balance = self.get_balance() + amount
        new_record = AccountRecord(action=AccountRecord.WITHDRAWL, balance=balance, time_at=None)
        self.histories.append(new_record)
        self.new_histories.append(new_record)

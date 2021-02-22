from datetime import datetime, timedelta
from typing import Dict, List, Optional

from account.entity import Account, Card, AccountRecord
from account.adaptors.account_repo import AccountRepository
from account.adaptors.session_manager import SessionManager


class FakeSessionmanager(SessionManager):
    def __init__(self, expire_seconds=120):
        self.session_storage = dict()
        self.session_expire_at = dict()
        self.session_counter = 0
        self.expire_seconds = expire_seconds

    def set_session(self, user_id: int) -> str:
        self.session_storage[user_id] = str(self.session_counter)
        self.session_counter += 1
        self.session_expire_at[user_id] = datetime.utcnow() + timedelta(seconds=self.expire_seconds)

    def validate_user_session(self, user_id: int, session_key: str) -> bool:
        if user_id not in self.session_expire_at:
            return False

        if datetime.utcnow() > self.session_expire_at[user_id]:
            return False

        return self.session_storage[user_id]  == session_key

    def extend_session(self, user_id: int):
        self.session_expire_at[user_id] = datetime.utcnow() + timedelta(seconds=self.expire_seconds)


class FakeAccountRepo(AccountRepository):
    def __init__(self, cards: List[Card], accounts: List[Account]):
        self.cards: Dict[int, Card] = {card.card_num: card for card in cards}
        self.accounts: Dict[int, Account] = {account.account_id: account for account in accounts}

    def get_card(self, card_num: int) -> Optional[Card]:
        if card_num not in self.cards:
            return None

        return self.cards[card_num]

    def view_user_accounts(self, user_id: int) -> List[Account]:
        return [account for _, account in self.accounts.items() if account.user_id == user_id]

    def _get_user_account(self, user_id: int, account_id: int) -> Optional[Account]:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        if account.user_id != user_id:
            return None

        return account

    def update_account(self, account_id: int, record: AccountRecord):
        self.accounts[account_id].histories.append(record)
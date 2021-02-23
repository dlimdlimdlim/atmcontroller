from typing import Optional
from datetime import datetime


class AccountRecord:
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'

    def __init__(self, action: str, balance: int, record_index: int, time_at: Optional[datetime] = None):
        if action != self.DEPOSIT and action != self.WITHDRAWAL:
            raise ValueError(f'invalid action {action}. Action must be "deposit" or "withdrawal"')

        self.record_index = record_index
        self.action = action
        self.balance = balance
        self.time_at = time_at

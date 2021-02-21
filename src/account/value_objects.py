from typing import Optional
from datetime import datetime


class AccountRecord:
    DEPOST = 'deposit'
    WITHDRAWL = 'withdrawl'

    def __init__(self, action: str, balance: int, time_at: Optional[datetime] = None):
        if action != self.DEPOST or action != self.WITHDRAWL:
            raise ValueError(f'invalid action {action}. Action must be "deposit" or "withdrawl"')

        self.action = action
        self.time_at = time_at
        self.balance = balance


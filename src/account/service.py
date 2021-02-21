import uuid

from account.value_objects import AccountRecord


def get_session(card_num: int, pin: int, uow):
    with uow:
        card = uow.account_data.get_card(card_num)
        if not card.validate_pin(pin):
            return None

        session_key = uow.account_data.set_session(card.user_id)
        return session_key


def get_accounts(session_key: str, card_num: int, uow):
    with uow:
        user = uow.account_data.get_user_by_card(card_num)
        if user.session_key != session_key:
            raise

        accounts = uow.account_data.get_user_accounts(user.id)
        return accounts


def _account_action(session_key: str, account_id: int, action: str, amount: int, card_num: int, uow):
    with uow:
        user = uow.account_data.get_user_by_card(card_num)
        if user.session_key != session_key:
            raise

        account = uow.account_data.get_account(user.id, account_id)
        if not account:
            raise

        if action == AccountRecord.DEPOST:
            account.deposit(amount)

        elif action == AccountRecord.WITHDRAWL:
            account.withdrawl(amount)
        else:
            raise


def deposit(session_key: str, account_id: int, amount: int, card_num: int, uow):
    return _account_action(session_key, account_id, AccountRecord.DEPOST, amount, card_num, uow)


def withdrawal(session_key: str, account_id: int, amount: int, card_num: int, uow):
    return _account_action(session_key, account_id, AccountRecord.WITHDRAWL, amount, card_num, uow)
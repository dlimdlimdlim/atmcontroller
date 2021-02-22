from account.value_objects import AccountRecord
from account.service import service_exceptions
from account.adaptors.session_manager import SessionManager
from account.service.unit_of_work import UnitOfWork


def set_session(card_num: int, pin: str, uow: UnitOfWork, session_manager: SessionManager):
    with uow:
        card = uow.account_data.get_card(card_num)
        if not card:
            raise service_exceptions.InvalidCardNum(f'card with number {card_num} does not exist!')

        if not card.validate_pin(pin):
            raise service_exceptions.IncorrectPin('Invalild pin code!')

        session_key = session_manager.set_session(card.user_id)
        return session_key


def get_accounts(session_key: str, card_num: int, uow: UnitOfWork, session_manager: SessionManager):
    with uow:
        card = uow.account_data.get_card(card_num)
        if not card:
            raise service_exceptions.InvalidCardNum(f'card with number {card_num} does not exist!')

        if not session_manager.validate_user_session(card.user_id, session_key):
            raise service_exceptions.InvalidSesionKey(f'seession key {session_key} is invalid!')

        accounts = uow.account_data.get_user_accounts(card.user_id)
        session_manager.extend_session(card.user_id)
        return accounts


def account_action(
        session_key: str,
        account_id: int,
        action: str, amount: int,
        card_num: int, uow: UnitOfWork,
        session_manager: SessionManager
):
    with uow:
        card = uow.account_data.get_card(card_num)
        if not card:
            raise service_exceptions.InvalidCardNum(f'card with number {card_num} does not exist!')

        if not session_manager.validate_user_session(card.user_id, session_key):
            raise service_exceptions.InvalidSesionKey(f'seession key {session_key} is invalid!')

        account = uow.account_data.get_user_account(card.user_id, account_id)

        if action == AccountRecord.DEPOSIT:
            account.deposit(amount)

        elif action == AccountRecord.WITHDRAWAL:
            account.withdraw(amount)
        else:
            raise ValueError('action must be either "deposit" or "withdrawal"')

        uow.account_data.update_account(account)
        session_manager.extend_session(card.user_id)
